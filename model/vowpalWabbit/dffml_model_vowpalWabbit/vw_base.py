# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Base class for VW models
"""
import os
import json
import hashlib
from pathlib import Path
from typing import AsyncIterator, Tuple, Any, NamedTuple

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, r2_score

from dffml.repo import Repo
from dffml.accuracy import Accuracy
from dffml.source.source import Sources
from dffml.feature.feature import Features, Feature
from dffml.model.model import ModelConfig, ModelContext, Model, ModelNotTrained


class VWConfig(ModelConfig, NamedTuple):
    directory: str
    predict: Feature
    features: Features


class VWContext(ModelContext):
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
                if k not in ["directory", "features", "predict"]
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
        config = self.parent.config._asdict()
        temp_config = {
            "directory": config["directory"],
            "predict": config["predict"],
            "features": config["features"],
        }
        del config["directory"]
        del config["predict"]
        del config["features"]
        if os.path.isfile(self._filename()):
            self.clf = self.parent.VW_MODEL(**config)
            self.clf.load(self._filename())
            config.update(temp_config)
        else:
            del temp_config
            self.clf = self.parent.VW_MODEL(**config)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def train(self, sources: Sources):
        data = []
        async for repo in sources.with_features(
            self.features + [self.parent.config.predict.NAME]
        ):
            feature_data = repo.features(
                self.features + [self.parent.config.predict.NAME]
            )
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = np.array(df.drop([self.parent.config.predict.NAME], 1))
        ydata = np.array(df[self.parent.config.predict.NAME])
        self.logger.info("Number of input repos: {}".format(len(xdata)))
        self.clf.fit(xdata, ydata)
        self.clf.save(self._filename())

    async def accuracy(self, sources: Sources) -> Accuracy:
        if not os.path.isfile(self._filename()):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        data = []
        async for repo in sources.with_features(self.features):
            feature_data = repo.features(
                self.features + [self.parent.config.predict.NAME]
            )
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = np.array(df.drop([self.parent.config.predict.NAME], 1))
        ydata = np.array(df[self.parent.config.predict.NAME])
        self.logger.debug("Number of input repos: {}".format(len(xdata)))
        y_pred = self.clf.predict(xdata)

        # TODO VW doesn't have scorer, need to build it
        self.confidence = r2_score(ydata, y_pred)
        self.logger.debug("Model Accuracy: {}".format(self.confidence))
        return self.confidence

    async def predict(
        self, repos: AsyncIterator[Repo]
    ) -> AsyncIterator[Tuple[Repo, Any, float]]:
        if not os.path.isfile(self._filename()):
            raise ModelNotTrained("Train model before prediction.")
        async for repo in repos:
            feature_data = repo.features(self.features)
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
            repo.predicted(
                target, self.clf.predict(predict)[0], self.confidence
            )
            yield repo


class VWModel(Model):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.saved = {}

    def _filename(self):
        return os.path.join(
            self.config.directory,
            hashlib.sha384(self.config.predict.NAME.encode()).hexdigest()
            + ".json",
        )

    async def __aenter__(self) -> "VWModel":
        path = Path(self._filename())
        if path.is_file():
            self.saved = json.loads(path.read_text())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        Path(self._filename()).write_text(json.dumps(self.saved))
