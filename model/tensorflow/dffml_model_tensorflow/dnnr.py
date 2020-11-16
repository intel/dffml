"""
Uses Tensorflow to create a generic DNN which learns on all of the features in a
record.
"""
import os
import importlib
from typing import Dict, Any, AsyncIterator

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from dffml.base import config
from dffml.record import Record
from dffml.model.model import Model
from dffml.model.accuracy import Accuracy
from dffml.util.entrypoint import entrypoint
from dffml.source.source import Sources, SourcesContext

from .dnnc import TensorflowModelContext, TensorflowBaseConfig


@config
class DNNRegressionModelConfig(TensorflowBaseConfig):
    pass


class DNNRegressionModelContext(TensorflowModelContext):
    """
    Model using tensorflow to make predictions. Handels creation of feature
    columns for real valued, string, and list of real valued features.
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.tf = importlib.import_module("tensorflow")
        self.np = importlib.import_module("numpy")
        self.model_dir_path = self._model_dir_path()
        self.all_features = self.parent.config.features.names() + [
            self.parent.config.predict.name
        ]
        self.features = self._applicable_features()

    @property
    def model(self):
        """
        Generates or loads a model
        """
        if self._model is not None:
            return self._model
        self.logger.debug("Loading model ")

        self._model = self.tf.compat.v1.estimator.DNNRegressor(
            feature_columns=list(self.feature_columns.values()),
            hidden_units=self.parent.config.hidden,
            model_dir=self.model_dir_path,
        )

        return self._model

    async def sources_to_array(self, sources: Sources):
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        y_cols = []

        async for record in sources.with_features(self.all_features):
            for feature, results in record.features(self.features).items():

                x_cols[feature].append(self.np.array(results))
            y_cols.append(record.feature(self.parent.config.predict.name))

        y_cols = self.np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = self.np.array(x_cols[feature])

        return x_cols, y_cols

    async def training_input_fn(
        self,
        sources: Sources,
        batch_size=20,
        shuffle=False,
        epochs=1,
        **kwargs,
    ):
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
            batch_size=batch_size,
            shuffle=shuffle,
            num_epochs=epochs,
            **kwargs,
        )
        return input_fn

    async def evaluate_input_fn(
        self,
        sources: Sources,
        batch_size=20,
        shuffle=False,
        epochs=1,
        **kwargs,
    ):
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
            batch_size=batch_size,
            shuffle=shuffle,
            num_epochs=epochs,
            **kwargs,
        )
        return input_fn

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input records
        as test data.
        """
        if not os.path.isdir(self.model_dir_path):
            raise NotADirectoryError("Model not trained")
        input_fn = await self.evaluate_input_fn(
            sources, batch_size=20, shuffle=False, epochs=1
        )
        metrics = self.model.evaluate(input_fn=input_fn)
        return Accuracy(1 - metrics["loss"])  # 1 - mse

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:
        """
        Uses trained data to make a prediction about the quality of a record.
        """
        predict, predictions, target = await self.get_predictions(sources)
        for record, pred_dict in zip(predict, predictions):
            # TODO Instead of float("nan") save accuracy value and use that.
            record.predicted(
                target, float(pred_dict["predictions"]), float("nan")
            )
            yield record


@entrypoint("tfdnnr")
class DNNRegressionModel(Model):
    """
    Implemented using Tensorflow's DNNEstimator.

    Usage:

    * predict: Name of the feature we are trying to predict or using for training.

    Generating train and test data

    * This creates files `train.csv` and `test.csv`,
      make sure to take a BACKUP of files with same name in the directory
      from where this command is run as it overwrites any existing files.

    .. literalinclude:: /../model/tensorflow/examples/tfdnnr/train_data.sh

    .. literalinclude:: /../model/tensorflow/examples/tfdnnr/test_data.sh

    Train the model

    .. literalinclude:: /../model/tensorflow/examples/tfdnnr/train.sh

    Assess the accuracy

    .. literalinclude:: /../model/tensorflow/examples/tfdnnr/accuracy.sh

    Output

    .. code-block::

        0.9468210011

    Make a prediction

    .. literalinclude:: /../model/tensorflow/examples/tfdnnr/predict.sh

    Output

    .. code-block:: json

        [
            {
                "extra": {},
                "features": {
                    "Feature1": 0.21,
                    "Feature2": 0.18,
                    "TARGET": 0.84
                },
                "last_updated": "2019-10-24T15:26:41Z",
                "prediction": {
                    "TARGET" : {
                        "confidence": null,
                        "value": 1.1983429193496704
                    }
                },
                "key": 0
            }
        ]

    Example usage of Tensorflow DNNEstimator model using python API

    .. literalinclude:: /../model/tensorflow/examples/tfdnnr/tfdnnr.py

    The ``null`` in ``confidence`` is the expected behaviour. (See TODO in
    predict).

    """

    CONTEXT = DNNRegressionModelContext
    CONFIG = DNNRegressionModelConfig
