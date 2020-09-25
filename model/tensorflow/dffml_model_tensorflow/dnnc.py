"""
Uses Tensorflow to create a generic DNN which learns on all of the features in a
record.
"""
import os
import abc
import hashlib
import inspect
import pathlib

import importlib

from dataclasses import dataclass
from typing import List, Dict, Any, AsyncIterator, Type


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from dffml.record import Record
from dffml.model.accuracy import Accuracy
from dffml.base import config, field
from dffml.util.entrypoint import entrypoint
from dffml.feature.feature import Feature, Features
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelContext, Model, ModelNotTrained


@dataclass
class TensorflowBaseConfig:
    predict: Feature = field("Feature name holding target values")
    features: Features = field("Features to train on")
    directory: pathlib.Path = field("Directory where state should be saved")
    steps: int = field("Number of steps to train the model", default=3000)
    epochs: int = field(
        "Number of iterations to pass over all records in a source", default=30
    )
    hidden: List[int] = field(
        "List length is the number of hidden layers in the network. Each entry in the list is the number of nodes in that hidden layer",
        default_factory=lambda: [12, 40, 15],
    )


class TensorflowModelContext(ModelContext):
    """
    Tensorflow based model contexts should derive from this model context. As it
    provides much of the bootstrapping such as mapping data types to feature
    columns.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.tf = importlib.import_module("tensorflow")
        self.np = importlib.import_module("numpy")
        self._model = None
        self.feature_columns = self._feature_columns()
        self.features = self._applicable_features()

    def _feature_columns(self):
        """
        Converts records into training data
        """
        cols: Dict[str, Any] = {}
        for feature in self.parent.config.features:
            col = self._feature_feature_column(feature)
            if not col is None:
                cols[feature.name] = col
        return cols

    def _feature_feature_column(self, feature: Feature):
        """
        Creates a feature column for a feature
        """
        dtype = feature.dtype
        if not inspect.isclass(dtype):
            self.logger.warning(
                "Unknown dtype %r. Cound not create column" % (dtype)
            )
            return None
        if (
            dtype is int
            or issubclass(dtype, int)
            or dtype is float
            or issubclass(dtype, float)
        ):
            return self.tf.feature_column.numeric_column(
                feature.name, shape=feature.length
            )
        self.logger.warning(
            "Unknown dtype %r. Cound not create column" % (dtype)
        )
        return None

    def _applicable_features(self):
        return [
            name
            for name in self.parent.config.features.names()
            if name in self.feature_columns
        ]

    def _model_dir_path(self):
        """
        Creates the path to the model dir by using the provided model dir and
        the sha384 hash of the concatenated feature names.
        """
        if self.parent.config.directory is None:
            return None
        _to_hash = self.features + list(map(str, self.parent.config.hidden))
        model = "DNNModel"
        if not os.path.isdir(self.parent.config.directory):
            raise NotADirectoryError(
                "%s is not a directory" % (self.parent.config.directory)
            )
        return os.path.join(self.parent.config.directory, model)

    async def predict_input_fn(self, sources: SourcesContext, **kwargs):
        """
        Uses the numpy input function with data from record features.
        """
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        ret_records = []
        async for record in sources.with_features(self.features):
            ret_records.append(record)
            for feature, results in record.features(self.features).items():
                x_cols[feature].append(self.np.array(results))
        for feature in x_cols:
            x_cols[feature] = self.np.array(x_cols[feature])
        self.logger.info("------ Record Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("-----------------------")
        input_fn = self.tf.compat.v1.estimator.inputs.numpy_input_fn(
            x_cols, shuffle=False, num_epochs=1, **kwargs
        )
        return input_fn, ret_records

    async def train(self, sources: Sources):
        """
        Train on data submitted via classify.
        """
        input_fn = await self.training_input_fn(sources)
        self.model.train(input_fn=input_fn, steps=self.parent.config.steps)

    async def get_predictions(self, sources: SourcesContext):
        if not os.path.isdir(self.model_dir_path):
            raise ModelNotTrained("Train model before prediction.")
        # Create the input function
        input_fn, predict = await self.predict_input_fn(sources)
        # Makes predictions on classifications
        predictions = self.model.predict(input_fn=input_fn)
        target = self.parent.config.predict.name

        return predict, predictions, target

    @property
    @abc.abstractmethod
    def model(self):
        """
        Create the model and return the handle to it.
        """


@config
class DNNClassifierModelConfig(TensorflowBaseConfig):
    classifications: List[str] = field(
        "Options for value of classification", default=None
    )
    clstype: Type = field("Data type of classifications values", default=str)
    batchsize: int = field(
        "Number records to pass through in an epoch", default=20
    )
    shuffle: bool = field(
        "Randomise order of records in a batch", default=True
    )

    def __post_init__(self):
        self.classifications = list(map(self.clstype, self.classifications))


class DNNClassifierModelContext(TensorflowModelContext):
    """
    Model using tensorflow to make predictions. Handels creation of feature
    columns for real valued, string, and list of real valued features.
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.cids = self._mkcids(self.parent.config.classifications)
        self.classifications = self._classifications(self.cids)
        self.model_dir_path = self._model_dir_path()

    def _mkcids(self, classifications):
        """
        Create an index, possible predict mapping and sort the list of
        classifications first.
        """
        cids = dict(
            zip(range(0, len(classifications)), sorted(classifications))
        )
        self.logger.debug("cids(%d): %r", len(cids), cids)
        return cids

    def _classifications(self, cids):
        """
        Map classifications to numeric values
        """
        classifications = {value: key for key, value in cids.items()}
        self.logger.debug(
            "classifications(%d): %r", len(classifications), classifications
        )
        return classifications

    @property
    def model(self):
        """
        Generates or loads a model
        """
        if self._model is not None:
            return self._model
        self.logger.debug(
            "Loading model with classifications(%d): %r",
            len(self.classifications),
            self.classifications,
        )
        self._model = self.tf.compat.v1.estimator.DNNClassifier(
            feature_columns=list(self.feature_columns.values()),
            hidden_units=self.parent.config.hidden,
            n_classes=len(self.parent.config.classifications),
            model_dir=self.model_dir_path,
        )
        return self._model

    async def sources_to_array(self, sources: Sources):
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        y_cols = []
        for record in [
            record
            async for record in sources.with_features(
                self.features + [self.parent.config.predict.name]
            )
            if self.parent.config.clstype(
                record.feature(self.parent.config.predict.name)
            )
            in self.classifications
        ]:
            for feature, results in record.features(self.features).items():
                x_cols[feature].append(self.np.array(results))
            y_cols.append(
                self.classifications[
                    self.parent.config.clstype(
                        record.feature(self.parent.config.predict.name)
                    )
                ]
            )
        if not y_cols:
            raise ValueError("No records to train on")
        y_cols = self.np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = self.np.array(x_cols[feature])

        return x_cols, y_cols

    async def training_input_fn(self, sources: Sources, **kwargs):
        """
        Uses the numpy input function with data from record features.
        """
        self.logger.debug("Training on features: %r", self.features)
        x_cols, y_cols = await self.sources_to_array(sources)
        self.logger.info("------ Record Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")
        input_fn = self.tf.compat.v1.estimator.inputs.numpy_input_fn(
            x_cols,
            y_cols,
            batch_size=self.parent.config.batchsize,
            shuffle=self.parent.config.shuffle,
            num_epochs=self.parent.config.epochs,
            **kwargs,
        )
        return input_fn

    async def accuracy_input_fn(self, sources: Sources, **kwargs):
        """
        Uses the numpy input function with data from record features.
        """
        x_cols, y_cols = await self.sources_to_array(sources)
        self.logger.info("------ Record Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")
        input_fn = self.tf.compat.v1.estimator.inputs.numpy_input_fn(
            x_cols,
            y_cols,
            batch_size=self.parent.config.batchsize,
            shuffle=self.parent.config.shuffle,
            num_epochs=1,
            **kwargs,
        )
        return input_fn

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input records
        as test data.
        """
        if not os.path.isdir(self.model_dir_path):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        input_fn = await self.accuracy_input_fn(sources)
        accuracy_score = self.model.evaluate(input_fn=input_fn)
        return Accuracy(accuracy_score["accuracy"])

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:
        """
        Uses trained data to make a prediction about the quality of a record.
        """
        predict, predictions, target = await self.get_predictions(sources)
        for record, pred_dict in zip(predict, predictions):
            class_id = pred_dict["class_ids"][0]
            probability = pred_dict["probabilities"][class_id]
            record.predicted(target, self.cids[class_id], probability)
            yield record


@entrypoint("tfdnnc")
class DNNClassifierModel(Model):
    """
    Implemented using Tensorflow's DNNClassifier.

    First we create the training and testing datasets

    .. literalinclude:: /../model/tensorflow/examples/tfdnnc/train_data.sh

    .. literalinclude:: /../model/tensorflow/examples/tfdnnc/test_data.sh

    Train the model

    .. literalinclude:: /../model/tensorflow/examples/tfdnnc/train.sh

    Assess the accuracy

    .. literalinclude:: /../model/tensorflow/examples/tfdnnc/accuracy.sh

    Output

    .. code-block::

        0.99996233782

    Make a prediction

    .. literalinclude:: /../model/tensorflow/examples/tfdnnc/predict.sh

    Output

    .. code-block:: json

        [
            {
                "extra": {},
                "features": {
                    "PetalLength": 4.2,
                    "PetalWidth": 1.5,
                    "SepalLength": 5.9,
                    "SepalWidth": 3.0,
                    "classification": 1
                },
                "last_updated": "2019-07-31T02:00:12Z",
                "prediction": {
                    "classification":
                        {
                            "confidence": 0.9999997615814209,
                            "value": 1
                        }
                },
                "key": "0"
            },
        ]

    Example usage of Tensorflow DNNClassifier model using python API

    .. literalinclude:: /../model/tensorflow/examples/tfdnnc/tfdnnc.py

    """

    CONTEXT = DNNClassifierModelContext
    CONFIG = DNNClassifierModelConfig
