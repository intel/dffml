# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import abc
import inspect
from typing import AsyncIterator, Tuple, Any, List, Optional, NamedTuple, Type
import os
import hashlib

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
from dffml.repo import Repo
from dffml.source.source import Sources
from dffml.feature import Features
from dffml.accuracy import Accuracy
from dffml.model.model import ModelConfig, ModelContext, Model
from dffml.util.entrypoint import entrypoint
from dffml.base import BaseConfig, config, field
from dffml.feature.feature import Feature, Features
from dffml_model_tensorflow.dnnc import TensorflowModelContext
import tensorflow as tf
import tensorflow
from dffml.model.model import ModelNotTrained
from tensorflow.keras.callbacks import ModelCheckpoint
import numpy as np
import tensorflow_hub as hub
import pandas as pd
from dffml_model_tensorflow_hub.tfhub_models import (
    bert_tokenizer,
    BertClassifier,
    NnlmClassifier,
)

tf.config.optimizer.set_jit(True)


@config
class TextClassifierConfig:
    predict: Feature = field("Feature name holding classification value")
    classifications: List[str] = field("Options for value of classification")
    features: Features = field("Features to train on")
    trainable: str = True
    preprocess: str = True
    batch_size: int = field("Batch size", default=120)
    max_seq_length: int = field("length of sentence", default=256)
    add_layers: bool = field("add layers", default=False)
    modelArchitecture: str = field(
        "Architecture type of pretrained model", default="bert"
    )
    layers: List[str] = field(
        "Extra layers added on top of pretrained model", default=None
    )
    pretrainedModeloutShape: int = field(
        "Shape of output  of pretrained model", default=768
    )
    inputShape: int = None

    model_path: str = field(
        "Pretrained model", default="/home/himanshu/Downloads/1 (3) (1)",
    )
    optimizer: str = field("Optimizer used by model", default="adam")
    metrics: str = field("Metric used to evaluate model", default="accuracy")

    clstype: Type = field("Data type of classifications values", default=str)
    epochs: int = field(
        "Number of iterations to pass over all repos in a source", default=1
    )

    directory: str = field(
        "Directory where state should be saved",
        default=os.path.join(
            os.path.expanduser("~"), ".cache", "dffml", "tensorflow_hub"
        ),
    )

    def __post_init__(self):
        self.classifications = list(map(self.clstype, self.classifications))
        if self.add_layers:
            self.layers = ["tf.keras.layers." + layer for layer in self.layers]
            self.layers = list(map(eval, self.layers))


class TextClassifierContext(TensorflowModelContext):
    """
    Model wraping model_name API
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.cids = self._mkcids(self.parent.config.classifications)
        self.classifications = self._classifications(self.cids)
        self.features = self._applicable_features()
        self.model_dir_path = self._model_dir_path()
        self._model = None

    async def __aenter__(self):

        path = self._model_dir_path()

        if os.path.isfile(os.path.join(path, "saved_model.pb")):
            self.logger.info("Using saved model")
            self._model = tf.keras.models.load_model(os.path.join(path))

            if self.parent.config.modelArchitecture == "bert":
                self.vocab_file = self._model.vocab_file.asset_path.numpy()
                self.do_lower_case = self._model.do_lower_case.numpy()
        else:
            self._model = self.createModel()

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    @property
    def classification(self):
        return self.parent.config.predict.NAME

    def _applicable_features(self):
        return [name for name in self.parent.config.features.names()]

    def _model_dir_path(self):
        if self.parent.config.directory is None:
            return None
        _to_hash = self.features + [
            self.classification,
            str(len(self.cids)),
            self.parent.config.modelArchitecture,
        ]
        model = hashlib.sha384("".join(_to_hash).encode("utf-8")).hexdigest()
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
        Generates or loads a model
        """
        if self._model is not None:
            return self._model
        self.logger.debug(
            "Loading model with classifications(%d): %r",
            len(self.classifications),
            self.classifications,
        )

        all_layers = []
        inputs = []

        if self.parent.config.modelArchitecture == "bert":

            bert = BertClassifier(self.parent.config)
            default_model = bert.load_model()
            self.mainLayer, self.vocab_file, self.do_lower_case = (
                bert.mainLayer,
                bert.vocab_file,
                bert.do_lower_case,
            )
            all_layers = [self.mainLayer] + (
                self.parent.config.layers
                if self.parent.config.add_layers
                else []
            )

        elif self.parent.config.modelArchitecture == "nnlm":

            nnlm = NnlmClassifier(self.parent.config)
            default_model = nnlm.load_model()
            self.mainLayer = nnlm.mainLayer

            all_layers = [self.mainLayer] + (
                self.parent.config.layers
                if self.parent.config.add_layers
                else []
            )

        if self.parent.config.add_layers:
            self._model = tf.keras.Sequential(all_layers)
        else:
            self._model = default_model

        self._model.compile(
            optimizer=self.parent.config.optimizer,
            loss="sparse_categorical_crossentropy",
            metrics=[self.parent.config.metrics],
        )
        # if not list(self._model.layers[-1].output_shape) == [None, len(self.cids)]:
        #     raise NameError("Output shape of last layer should be:", (None, len(self.cids)))
        return self._model

    async def train_data_generator(
        self, sources: Sources, **kwargs,
    ):
        """
        Uses the numpy input function with data from repo features.
        """
        self.logger.debug("Training on features: %r", self.features)
        x_cols: Dict[str, Any] = {feature: [] for feature in self.features}
        y_cols = []
        all_repos = []
        all_sources = sources.with_features(
            self.features + [self.classification]
        )
        async for repo in all_sources:
            if repo.feature(self.classification) in self.classifications:
                all_repos.append(repo)
        for repo in all_repos:
            for feature, results in repo.features(self.features).items():
                x_cols[feature].append(np.array(results))
            y_cols.append(
                self.classifications[repo.feature(self.classification)]
            )
        if not y_cols:
            raise ValueError("No repos to train on")
        y_cols = np.array(y_cols)
        for feature in x_cols:
            x_cols[feature] = np.array(x_cols[feature])
        self.logger.info("------ Repo Data ------")
        self.logger.info("x_cols:    %d", len(list(x_cols.values())[0]))
        self.logger.info("y_cols:    %d", len(y_cols))
        self.logger.info("-----------------------")

        if self.parent.config.preprocess:
            if self.parent.config.modelArchitecture == "bert":
                if (len(self.features)) > 1:
                    self.logger.critical(
                        "Bert Found more than one feature to train on. Only first feature will be used"
                    )
                x_cols = bert_tokenizer(
                    x_cols[self.features[0]],
                    self.parent.config.max_seq_length,
                    self.vocab_file,
                    self.do_lower_case,
                )
                x_cols = dict(
                    input_word_ids=x_cols[0],
                    input_mask=x_cols[1],
                    segment_ids=x_cols[2],
                )
            if self.parent.config.modelArchitecture == "nnlm":
                x_cols = tf.convert_to_tensor(x_cols[self.features[0]])
        return x_cols, y_cols

    async def prediction_data_generator(
        self, x_cols, **kwargs,
    ):

        if self.parent.config.modelArchitecture == "bert":
            if (len(self.features)) > 1:
                self.logger.critical(
                    "Bert Found more than one feature. Only first feature will be used for prediction"
                )
            x_cols = bert_tokenizer(
                x_cols,
                self.parent.config.max_seq_length,
                self.vocab_file,
                self.do_lower_case,
            )
            x_cols = dict(
                input_word_ids=x_cols[0],
                input_mask=x_cols[1],
                segment_ids=x_cols[2],
            )
        return x_cols

    async def train(self, sources: Sources):
        """
        Train using repos as the data to learn from.
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
        if self.parent.config.modelArchitecture == "bert":
            self._model.vocab_file = tf.saved_model.Asset(self.vocab_file)
            self._model.do_lower_case = tf.Variable(self.do_lower_case)

        tf.keras.models.save_model(self._model, self._model_dir_path())

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input repos
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
        self, repos: AsyncIterator[Repo]
    ) -> AsyncIterator[Tuple[Repo, Any, float]]:
        """
        Uses trained data to make a prediction about the quality of a repo.
        """
        if not os.path.isfile(
            os.path.join(self.model_dir_path, "saved_model.pb")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")

        async for repo in repos:
            feature_data = repo.features(self.features)
            df = pd.DataFrame(feature_data, index=[0])
            predict = await self.prediction_data_generator(np.array(df)[0])
            all_prob = self._model.predict(predict)
            max_prob_idx = all_prob.argmax(axis=-1)
            self.logger.debug(
                "Predicted probability of {} for {}: {}".format(
                    self.parent.config.predict.NAME,
                    np.array(df)[0],
                    all_prob[0],
                )
            )

            repo.predicted(
                self.cids[max_prob_idx[0]], all_prob[0][max_prob_idx[0]]
            )
            yield repo


@entrypoint("text_classifier")
class TextClassificationModel(Model):

    CONTEXT = TextClassifierContext
    CONFIG = TextClassifierConfig
