# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Base class for Scikit models
"""
import os
import json
import hashlib
from pathlib import Path
from typing import AsyncIterator, Tuple, Any, NamedTuple

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score, mutual_info_score

from dffml.record import Record
from dffml.source.source import Sources
from dffml.model.accuracy import Accuracy
from dffml.model.model import ModelConfig, ModelContext, Model, ModelNotTrained
from dffml.feature.feature import Features, Feature


class ScikitConfig(ModelConfig, NamedTuple):
    directory: str
    predict: Feature
    features: Features
    tcluster: Feature


class ScikitContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.features = self.applicable_features(self.parent.config.features)
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
                if k not in ["directory", "features", "tcluster", "predict"]
            ]
        )
        return hashlib.sha384(
            "".join([params] + self.features).encode()
        ).hexdigest()

    def _filename(self):
        return os.path.join(
            self.parent.config.directory, self._features_hash + ".joblib"
        )

    async def __aenter__(self):
        if os.path.isfile(self._filename()):
            self.clf = joblib.load(self._filename())
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
        data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.NAME]
        ):
            feature_data = record.features(
                self.features + [self.parent.config.predict.NAME]
            )
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = np.array(df.drop([self.parent.config.predict.NAME], 1))
        ydata = np.array(df[self.parent.config.predict.NAME])
        self.logger.info("Number of input records: {}".format(len(xdata)))
        self.clf.fit(xdata, ydata)
        joblib.dump(self.clf, self._filename())

    async def accuracy(self, sources: Sources) -> Accuracy:
        if not os.path.isfile(self._filename()):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        data = []
        async for record in sources.with_features(self.features):
            feature_data = record.features(
                self.features + [self.parent.config.predict.NAME]
            )
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = np.array(df.drop([self.parent.config.predict.NAME], 1))
        ydata = np.array(df[self.parent.config.predict.NAME])
        self.logger.debug("Number of input records: {}".format(len(xdata)))
        self.confidence = self.clf.score(xdata, ydata)
        self.logger.debug("Model Accuracy: {}".format(self.confidence))
        return self.confidence

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not os.path.isfile(self._filename()):
            raise ModelNotTrained("Train model before prediction.")
        async for record in records:
            feature_data = record.features(self.features)
            df = pd.DataFrame(feature_data, index=[0])
            predict = np.array(df)
            self.logger.debug(
                "Predicted Value of {} for {}: {}".format(
                    self.parent.config.predict,
                    predict,
                    self.clf.predict(predict),
                )
            )
            target = self.parent.config.predict.NAME
            record.predicted(
                target, self.clf.predict(predict)[0], self.confidence
            )
            yield record


class ScikitContextUnsprvised(ScikitContext):
    async def __aenter__(self):
        if os.path.isfile(self._filename()):
            self.clf = joblib.load(self._filename())
        else:
            config = self.parent.config._asdict()
            del config["directory"]
            del config["features"]
            del config["tcluster"]
            del config["predict"]
            self.clf = self.parent.SCIKIT_MODEL(**config)
        return self

    async def train(self, sources: Sources):
        data = []
        async for record in sources.with_features(self.features):
            feature_data = record.features(self.features)
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = np.array(df)
        self.logger.info("Number of input records: {}".format(len(xdata)))
        self.clf.fit(xdata)
        joblib.dump(self.clf, self._filename())

    async def accuracy(self, sources: Sources) -> Accuracy:
        if not os.path.isfile(self._filename()):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        data = []
        target = []
        estimator_type = self.clf._estimator_type
        if estimator_type is "clusterer":
            target = (
                []
                if self.parent.config.tcluster is None
                else [self.parent.config.tcluster.NAME]
            )
        async for record in sources.with_features(self.features):
            feature_data = record.features(self.features + target)
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = np.array(df.drop(target, axis=1))
        self.logger.debug("Number of input records: {}".format(len(xdata)))
        if target:
            ydata = np.array(df[target]).flatten()
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
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        if not os.path.isfile(self._filename()):
            raise ModelNotTrained("Train model before prediction.")
        estimator_type = self.clf._estimator_type
        if estimator_type is "clusterer":
            if hasattr(self.clf, "predict"):
                # inductive clusterer
                predictor = self.clf.predict
            else:
                # transductive clusterer
                self.logger.critical(
                    "Predict found transductive clusterer, ensure data being passed is training data"
                )
                labels = [
                    (yield label) for label in self.clf.labels_.astype(np.int)
                ]
                predictor = lambda predict: [next(labels)]

        async for record in records:
            feature_data = record.features(self.features)
            df = pd.DataFrame(feature_data, index=[0])
            predict = np.array(df)
            prediction = predictor(predict)
            self.logger.debug(
                "Predicted cluster for {}: {}".format(predict, prediction)
            )
            target = self.parent.config.predict.NAME
            record.predicted(target, prediction[0], self.confidence)
            yield record


class Scikit(Model):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.saved = {}

    def _filename(self):
        return os.path.join(
            self.config.directory,
            hashlib.sha384(self.config.predict.NAME.encode()).hexdigest()
            + ".json",
        )

    async def __aenter__(self) -> "Scikit":
        path = Path(self._filename())
        if path.is_file():
            self.saved = json.loads(path.read_text())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        Path(self._filename()).write_text(json.dumps(self.saved))


class ScikitUnsprvised(Scikit):
    def _filename(self):
        model_name = self.SCIKIT_MODEL.__name__
        return os.path.join(
            self.config.directory,
            hashlib.sha384(
                (
                    "".join(
                        [model_name]
                        + sorted(
                            feature.NAME for feature in self.config.features
                        )
                    )
                ).encode()
            ).hexdigest()
            + ".json",
        )
