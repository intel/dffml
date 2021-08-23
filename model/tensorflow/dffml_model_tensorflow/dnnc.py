"""
Uses Tensorflow to create a generic DNN which learns on all of the features in a
record.
"""
import os
from typing import List, Dict, Any, AsyncIterator, Type


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from dffml.record import Record
from dffml.base import config, field
from dffml.util.entrypoint import entrypoint
from dffml.source.source import Sources, SourcesContext

from .tf_base import (
    TensorflowBaseConfig,
    TensorflowModelContext,
    TensorflowModel,
)


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

    async def sources_to_array(self, sources: Sources):
        x_cols: Dict[str, Any] = {
            feature: [] for feature in self.parent.features
        }
        y_cols = []
        for record in [
            record
            async for record in sources.with_features(
                self.parent.features + [self.parent.config.predict.name]
            )
            if self.parent.config.clstype(
                record.feature(self.parent.config.predict.name)
            )
            in self.parent.classifications
        ]:
            for feature, results in record.features(
                self.parent.features
            ).items():
                x_cols[feature].append(self.np.array(results))
            y_cols.append(
                self.parent.classifications[
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
        self.logger.debug("Training on features: %r", self.parent.features)
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

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:
        """
        Uses trained data to make a prediction about the quality of a record.
        """
        predict, predictions, target = await self.get_predictions(sources)
        for record, pred_dict in zip(predict, predictions):
            class_id = pred_dict["class_ids"][0]
            probability = pred_dict["probabilities"][class_id]
            record.predicted(target, self.parent.cids[class_id], probability)
            yield record


@entrypoint("tfdnnc")
class DNNClassifierModel(TensorflowModel):
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

    def __init__(self, config):
        super().__init__(config)
        self.cids = self._mkcids(self.config.classifications)
        self.classifications = self._classifications(self.cids)

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
            hidden_units=self.config.hidden,
            n_classes=len(self.config.classifications),
            model_dir=self.model_path,
        )
        return self._model
