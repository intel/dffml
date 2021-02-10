# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Base class for Scikit models
"""
import json
import hashlib
import pathlib
import logging
import importlib

from typing import AsyncIterator, Tuple, Any, NamedTuple

from sklearn.metrics import silhouette_score, mutual_info_score

# https://intelpython.github.io/daal4py/sklearn.html
try:
    import daal4py.sklearn

    daal4py.sklearn.patch_sklearn()
except ImportError:
    # Ignore import errors, package is not installed
    pass
except Execption as error:
    LOGGER = logging.getLogger(__package__)
    LOGGER.error(error)

from dffml.record import Record
from dffml.model.accuracy import Accuracy
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelConfig, ModelContext, Model, ModelNotTrained
from dffml.feature.feature import Features, Feature


class ScikitConfig(ModelConfig, NamedTuple):
    directory: pathlib.Path
    predict: Feature
    features: Features
    tcluster: Feature


class ScikitContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.np = importlib.import_module("numpy")
        self.joblib = importlib.import_module("joblib")
        self.features = self.parent.config.features.names()
        self._features_hash = self._feature_predict_hash()
        self.clf = None

    @property
    def confidence(self):
        return self.parent.saved.get(self._features_hash, float("nan"))

    @confidence.setter
    def confidence(self, confidence):
        self.parent.saved[self._features_hash] = confidence

    def _feature_predict_hash(self):
        params = "".join(
            [
                "{}{}".format(k, v)
                for k, v in self.parent.config._asdict().items()
                if k not in ["features", "tcluster", "predict"]
            ]
        )
        return hashlib.sha384(
            "".join([params] + self.features).encode()
        ).hexdigest()

    @property
    def _filepath(self):
        return self.parent.config.directory / "ScikitFeatures.joblib"

    async def __aenter__(self):
        if self._filepath.is_file():
            self.clf = self.joblib.load(str(self._filepath))
        else:
            config = self.parent.config._asdict()
            del config["directory"]
            del config["predict"]
            del config["features"]
            self.clf = self.parent.SCIKIT_MODEL(**config)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def train(self, sources: Sources):
        xdata = []
        ydata = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if self.np.isscalar(feature) else feature
                )
            xdata.append(record_data)
            ydata.append(record.feature(self.parent.config.predict.name))
        xdata = self.np.array(xdata)
        ydata = self.np.array(ydata)
        self.logger.info("Number of input records: {}".format(len(xdata)))
        self.clf.fit(xdata, ydata)
        self.joblib.dump(self.clf, str(self._filepath))

    async def accuracy(self, sources: Sources) -> Accuracy:
        if not self._filepath.is_file():
            raise ModelNotTrained("Train model before assessing for accuracy.")
        xdata = []
        ydata = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if self.np.isscalar(feature) else feature
                )
            xdata.append(record_data)
            ydata.append(record.feature(self.parent.config.predict.name))
        xdata = self.np.array(xdata)
        ydata = self.np.array(ydata)
        self.logger.debug("Number of input records: {}".format(len(xdata)))
        self.confidence = self.clf.score(xdata, ydata)
        self.logger.debug("Model Accuracy: {}".format(self.confidence))
        return self.confidence

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not self._filepath.is_file():
            raise ModelNotTrained("Train model before prediction.")
        async for record in sources.with_features(self.features):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if self.np.isscalar(feature) else feature
                )
            predict = self.np.array([record_data])
            self.logger.debug(
                "Predicted Value of {} for {}: {}".format(
                    self.parent.config.predict,
                    predict,
                    self.clf.predict(predict),
                )
            )
            target = self.parent.config.predict.name
            record.predicted(
                target,
                self.parent.config.predict.dtype(self.clf.predict(predict)[0])
                if self.parent.config.predict.dtype is not str
                else self.clf.predict(predict)[0],
                self.confidence,
            )
            yield record


class ScikitContextUnsprvised(ScikitContext):
    async def __aenter__(self):
        if self._filepath.is_file():
            self.clf = self.joblib.load(str(self._filepath))
        else:
            config = self.parent.config._asdict()
            del config["directory"]
            del config["features"]
            del config["tcluster"]
            del config["predict"]
            self.clf = self.parent.SCIKIT_MODEL(**config)
        return self

    async def train(self, sources: Sources):
        xdata = []
        async for record in sources.with_features(self.features):
            feature_data = record.features(self.features)
            xdata.append(list(feature_data.values()))
        xdata = self.np.array(xdata)
        self.logger.info("Number of input records: {}".format(len(xdata)))
        self.clf.fit(xdata)
        self.joblib.dump(self.clf, str(self._filepath))

    async def accuracy(self, sources: Sources) -> Accuracy:
        if not self._filepath.is_file():
            raise ModelNotTrained("Train model before assessing for accuracy.")
        xdata = []
        ydata = []
        target = []
        estimator_type = self.clf._estimator_type
        if estimator_type == "clusterer":
            target = (
                []
                if self.parent.config.tcluster is None
                else [self.parent.config.tcluster.name]
            )
        async for record in sources.with_features(self.features):
            feature_data = record.features(self.features)
            xdata.append(list(feature_data.values()))
            ydata.append(list(record.features(target).values()))
        xdata = self.np.array(xdata)
        self.logger.debug("Number of input records: {}".format(len(xdata)))
        if target:
            ydata = self.np.array(ydata).flatten()
            if hasattr(self.clf, "predict"):
                # xdata can be training data or unseen data
                # inductive clusterer with ground truth
                y_pred = self.clf.predict(xdata)
                self.confidence = mutual_info_score(ydata, y_pred)
            else:
                # requires xdata = training data
                # transductive clusterer with ground truth
                self.logger.critical(
                    "Accuracy found transductive clusterer, ensure data being passed is training data"
                )
                self.confidence = mutual_info_score(ydata, self.clf.labels_)
        else:
            if hasattr(self.clf, "predict"):
                # xdata can be training data or unseen data
                # inductive clusterer without ground truth
                y_pred = self.clf.predict(xdata)
                self.confidence = silhouette_score(xdata, y_pred)
            else:
                # requires xdata = training data
                # transductive clusterer without ground truth
                self.logger.critical(
                    "Accuracy found transductive clusterer, ensure data being passed is training data"
                )
                self.confidence = silhouette_score(xdata, self.clf.labels_)
        self.logger.debug("Model Accuracy: {}".format(self.confidence))
        return self.confidence

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not self._filepath.is_file():
            raise ModelNotTrained("Train model before prediction.")
        estimator_type = self.clf._estimator_type
        if estimator_type == "clusterer":
            if hasattr(self.clf, "predict"):
                # inductive clusterer
                predictor = self.clf.predict
            else:
                # transductive clusterer
                self.logger.critical(
                    "Predict found transductive clusterer, ensure data being passed is training data"
                )

                def yield_labels():
                    for label in self.clf.labels_.astype(self.np.int):
                        yield label

                labels = yield_labels()
                predictor = lambda predict: [next(labels)]
        else:
            raise NotImplementedError(
                f"Model is not a clusterer: {self.clf._estimator_type}"
            )

        async for record in sources.with_features(self.features):
            feature_data = record.features(self.features)
            predict = self.np.array([list(feature_data.values())])
            prediction = predictor(predict)
            self.logger.debug(
                "Predicted cluster for {}: {}".format(predict, prediction)
            )
            target = self.parent.config.predict.name
            record.predicted(
                target,
                self.parent.config.predict.dtype(prediction[0])
                if self.parent.config.predict.dtype is not str
                else prediction[0],
                self.confidence,
            )
            yield record


class Scikit(Model):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.saved = {}

    @property
    def _filepath(self):
        return self.config.directory / "Scikit.json"

    async def __aenter__(self) -> "Scikit":
        if self._filepath.is_file():
            self.saved = json.loads(self._filepath.read_text())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._filepath.write_text(json.dumps(self.saved))


class ScikitUnsprvised(Scikit):
    @property
    def _filepath(self):
        model_name = self.SCIKIT_MODEL.__name__
        return self.config.directory / "ScikitUnsupervised.json"
