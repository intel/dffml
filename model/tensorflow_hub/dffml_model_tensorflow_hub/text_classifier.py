# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
# TODO Add docstrings
import os
import hashlib
import pathlib
import importlib
from typing import AsyncIterator, Tuple, Any, List, Type


# should be set before importing tensorflow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from dffml.record import Record
from dffml.model.accuracy import Accuracy
from dffml.util.entrypoint import entrypoint
from dffml.base import config, field
from dffml.feature.feature import Feature, Features
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelContext, Model, ModelNotTrained
from dffml_model_tensorflow.util.config.tensorflow import parse_layers

from .tfhub_models import bert_tokenizer, ClassificationModel


class OutputShapeError(Exception):
    """
    Raised when number of nodes in last layer of tensorflow hub text_classifier
    are not equal to the number of classification categories.
    """


@config
class TextClassifierConfig:
    predict: Feature = field("Feature name holding classification value")
    classifications: List[str] = field("Options for value of classification")
    features: Features = field("Features to train on")
    directory: pathlib.Path = field("Directory where state should be saved")
    trainable: str = field(
        "Tweak pretrained model by training again", default=True
    )
    batch_size: int = field("Batch size", default=120)
    max_seq_length: int = field(
        "Length of sentence, used in preprocessing of input for bert embedding",
        default=256,
    )
    add_layers: bool = field(
        "Add layers on the top of pretrianed model/layer", default=False
    )
    embedType: str = field(
        "Type of pretrained embedding model, required to be set to `bert` to use bert pretrained embedding",
        default=None,
    )
    layers: List[str] = field(
        "Extra layers to be added on top of pretrained model", default=None
    )
    model_path: str = field(
        "Pretrained model path/url",
        default="https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim-with-oov/1",
    )
    optimizer: str = field("Optimizer used by model", default="adam")
    metrics: str = field("Metric used to evaluate model", default="accuracy")
    clstype: Type = field("Data type of classifications values", default=str)
    epochs: int = field(
        "Number of iterations to pass over all records in a source", default=10
    )

    def __post_init__(self):
        self.classifications = list(map(self.clstype, self.classifications))
        if self.add_layers:
            # Temperory solution
            self.layers = parse_layers(self.layers)


class TextClassifierContext(ModelContext):
    """
    Model wraping tensorflow hub pretrained embeddings
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.tf = importlib.import_module("tensorflow")
        self.np = importlib.import_module("numpy")
        self.pd = importlib.import_module("pandas")
        self.cids = self._mkcids(self.parent.config.classifications)
        self.classifications = self._classifications(self.cids)
        self.features = self._applicable_features()
        self.model_dir_path = self._model_dir_path()
        self._model = None

    async def __aenter__(self):
        path = self._model_dir_path()
        if os.path.isfile(os.path.join(path, "saved_model.pb")):
            self.logger.info(f"Using saved model from {path}")
            self._model = self.tf.keras.models.load_model(os.path.join(path))
        else:
            self._model = self.createModel()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def classification(self):
        return self.parent.config.predict.name

    def _applicable_features(self):
        return [name for name in self.parent.config.features.names()]

    def _model_dir_path(self):
        if self.parent.config.directory is None:
            return None
        _to_hash = self.features + [
            self.classification,
            str(len(self.cids)),
            self.parent.config.model_path,
        ]
        model = hashlib.sha384("".join(_to_hash).encode("utf-8")).hexdigest()
        # Needed to save updated model
        if not os.path.isdir(self.parent.config.directory):
            raise NotADirectoryError(
                "%s is not a directory" % (self.parent.config.directory)
            )
        os.makedirs(
            os.path.join(self.parent.config.directory, model), exist_ok=True
        )
        return os.path.join(self.parent.config.directory, model)

    def _mkcids(self, classifications):
        """
        Create an index, possible classification mapping and sort the list of
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
        return self._model

    def createModel(self):
        """
        Generates a model
        """
        if self._model is not None:
            return self._model
        self.logger.debug(
            "Loading model with classifications(%d): %r",
            len(self.classifications),
            self.classifications,
        )
        self._model = ClassificationModel(self.parent.config).load_model()
        self._model.compile(
            optimizer=self.parent.config.optimizer,
            loss="sparse_categorical_crossentropy",
            metrics=[self.parent.config.metrics],
        )

        if not list(self._model.layers[-1].output_shape) == [
            None,
            len(self.cids),
        ]:
            raise OutputShapeError(
                "Output shape of last layer should be:{}".format(
                    (None, len(self.cids))
                )
            )
        return self._model

    async def train_data_generator(self, sources: Sources):

        self.logger.debug("Training on features: %r", self.features)
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        y_cols = []
        all_records = []
        all_sources = sources.with_features(
            self.features + [self.classification]
        )
        async for record in all_sources:
            if record.feature(self.classification) in self.classifications:
                all_records.append(record)
        for record in all_records:
            for feature, results in record.features(self.features).items():
                x_cols[feature].append(self.np.array(results))
            y_cols.append(
                self.classifications[record.feature(self.classification)]
            )
        if not y_cols:
            raise ValueError("No records to train on")
        y_cols = self.np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = self.np.array(x_cols[feature])
        self.logger.info("------ Record Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")

        if (len(self.features)) > 1:
            self.logger.critical(
                "Found more than one feature to train on. Only first feature will be used"
            )
        # TODO add more embedTypes
        # so far only model available on tensorflow hub which requires special input preprocessing is `bert`
        if self.parent.config.embedType in ["bert"]:
            x_cols = bert_tokenizer(
                x_cols[self.features[0]],
                self.parent.config.max_seq_length,
                self._model.vocab_file.asset_path.numpy(),
                self._model.do_lower_case.numpy(),
            )
            x_cols = dict(
                input_word_ids=x_cols[0],
                input_mask=x_cols[1],
                segment_ids=x_cols[2],
            )
        else:
            # Universal Sentence Encoder, Neural Network Language Model, Swivel Embeddings
            # No preprocessing needed
            x_cols = x_cols[self.features[0]]
        return x_cols, y_cols

    async def prediction_data_generator(self, x_cols):
        if (len(self.features)) > 1:
            self.logger.critical(
                "Found more than one feature. Only first feature will be used for prediction"
            )
        if self.parent.config.embedType in ["bert"]:
            x_cols = bert_tokenizer(
                x_cols,
                self.parent.config.max_seq_length,
                self._model.vocab_file.asset_path.numpy(),
                self._model.do_lower_case.numpy(),
            )
            x_cols = dict(
                input_word_ids=x_cols[0],
                input_mask=x_cols[1],
                segment_ids=x_cols[2],
            )
        return x_cols

    async def train(self, sources: Sources):
        """
        Train using records as the data to learn from.
        """
        x, y = await self.train_data_generator(sources)
        self._model.summary()
        self._model.fit(
            x,
            y,
            epochs=self.parent.config.epochs,
            batch_size=self.parent.config.batch_size,
            verbose=1,
        )
        self.tf.keras.models.save_model(self._model, self._model_dir_path())

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input records
        as test data.
        """
        if not os.path.isfile(
            os.path.join(self.model_dir_path, "saved_model.pb")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        x, y = await self.train_data_generator(sources)
        accuracy_score = self._model.evaluate(x, y)
        return Accuracy(accuracy_score[1])

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        """
        Uses trained data to make a prediction about the quality of a record.
        """
        if not os.path.isfile(
            os.path.join(self.model_dir_path, "saved_model.pb")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")

        async for record in sources.with_features(self.features):
            feature_data = record.features(self.features)
            df = self.pd.DataFrame(feature_data, index=[0])
            predict = await self.prediction_data_generator(
                self.np.array(df)[0]
            )
            all_prob = self._model.predict(predict)
            max_prob_idx = all_prob.argmax(axis=-1)
            target = self.parent.config.predict.name
            self.logger.debug(
                "Predicted probability of {} for {}: {}".format(
                    self.parent.config.predict.name,
                    self.np.array(df)[0],
                    all_prob[0],
                )
            )

            record.predicted(
                target,
                self.cids[max_prob_idx[0]],
                all_prob[0][max_prob_idx[0]],
            )
            yield record


@entrypoint("text_classifier")
class TextClassificationModel(Model):
    """
    Implemented using Tensorflow hub pretrained models.

    
    .. literalinclude:: /../model/tensorflow_hub/examples/tfhub_text_classifier/train_data.sh

    .. literalinclude:: /../model/tensorflow_hub/examples/tfhub_text_classifier/test_data.sh

    Train the model

    .. literalinclude:: /../model/tensorflow_hub/examples/tfhub_text_classifier/train.sh

    Assess the accuracy

    .. literalinclude:: /../model/tensorflow_hub/examples/tfhub_text_classifier/accuracy.sh

    Output

    .. code-block::

        0.5

    Make a prediction

    .. literalinclude:: /../model/tensorflow_hub/examples/tfhub_text_classifier/predict.sh

    Output

    .. code-block:: json

        [
            {
                "extra": {},
                "features": {
                    "sentence": "I am not feeling good",
                    "sentiment": 0
                },
                "key": "0",
                "last_updated": "2020-05-14T20:14:30Z",
                "prediction": {
                    "sentiment": {
                        "confidence": 0.9999992847442627,
                        "value": 1
                    }
                }
            },
            {
                "extra": {},
                "features": {
                    "sentence": "Our trip was full of adventures",
                    "sentiment": 1
                },
                "key": "1",
                "last_updated": "2020-05-14T20:14:30Z",
                "prediction": {
                    "sentiment": {
                        "confidence": 0.9999088048934937,
                        "value": 1
                    }
                }
            }
        ]



    Example usage of Tensorflow_hub Text Classifier model using python API

    .. literalinclude:: /../model/tensorflow_hub/examples/tfhub_text_classifier/textclassifier.py
    """

    CONTEXT = TextClassifierContext
    CONFIG = TextClassifierConfig
