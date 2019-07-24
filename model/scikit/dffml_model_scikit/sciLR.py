# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import abc
import json
import hashlib
from typing import AsyncIterator, Tuple, Any, List, Optional, NamedTuple, Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from dffml.repo import Repo
from dffml.source.source import Sources
from dffml.feature import Features
from dffml.accuracy import Accuracy
from dffml.model.model import ModelConfig, ModelContext, Model
from dffml.util.entrypoint import entry_point
from dffml.util.cli.arg import Arg


class LRConfig(ModelConfig, NamedTuple):
    directory: str
    predict: str


class LRContext(ModelContext):

    def __init__(self, parent, features):
        super().__init__(parent, features)
        self.features = self.applicable_features(features)
        self.clf = None

    @property
    def confidence(self):
        return self.parent.saved.get(self._feature_predict_hash(), None)

    @confidence.setter
    def confidence(self, confidence):
        self.parent.saved[self._feature_predict_hash()] = confidence

    def _feature_predict_hash(self):
        return hashlib.sha384(''.join(self.features + [self.parent.config.predict]).encode()).hexdigest()

    def _filename(self):
        return os.path.join(
            self.parent.config.directory,
            self._feature_predict_hash() + '.joblib')

    async def __aenter__(self):
        if(os.path.isfile(self._filename())):
            self.clf = joblib.load(self._filename())
        else:
            self.clf = LinearRegression(n_jobs=-1)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        joblib.dump(self.clf, self._filename())

    def applicable_features(self, featuress):
        usable = []
        for feature in featuress:
            if feature.dtype() != int and feature.dtype() != float:
                raise ValueError("Linear Regression only supports int or float feature")
            if feature.length() != 1:
                raise ValueError("Linear Regression only supports single values (non-matrix / array)")
            usable.append(feature.NAME)
        return sorted(usable)

    async def train(self, sources: Sources):
        data = []
        async for repo in sources.with_features(self.features):
            feature_data = repo.features(self.features
                                         + [self.parent.config.predict])
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = np.array(df.drop([self.parent.config.predict], 1))
        ydata = np.array(df[self.parent.config.predict])
        self.logger.debug("Number of input repos: {}".format(len(xdata)))
        self.clf.fit(xdata, ydata)
        joblib.dump(self.clf, self._filename())

    async def accuracy(self, sources: Sources) -> Accuracy:
        if(os.path.isfile(self._filename())):
            data = []
            async for repo in sources.with_features(self.features):
                feature_data = repo.features(self.features
                                         + [self.parent.config.predict])
                data.append(feature_data)
            df = pd.DataFrame(data)
            xdata = np.array(df.drop([self.parent.config.predict], 1))
            ydata = np.array(df[self.parent.config.predict])
            self.logger.debug("Number of input repos: {}".format(len(xdata)))
            self.confidence = self.clf.score(xdata, ydata)
        else:
            raise ValueError('Model Not Trained')
        return self.confidence

    async def predict(self, repos: AsyncIterator[Repo]) -> \
                    AsyncIterator[Tuple[Repo, Any, float]]:
        if self.confidence is None:
            raise ValueError('Model Not Trained')
        async for repo in repos:
            feature_data = repo.features(self.features)
            df = pd.DataFrame(feature_data, index=[0])
            predict = np.array(df)
            self.logger.debug(
                "Predicted Value of {} for {}: {}".format(
                    self.parent.config.predict, predict, self.clf.predict(predict)
                )
            )
            yield repo, self.clf.predict(predict), self.confidence


@entry_point("sciLR")
class LR(Model):
    """
    Linear Regression Model implemented using scikit. Models are saved under the
    ``directory`` in subdirectories named after the hash of their feature names.
    """

    CONTEXT = LRContext

    def __init__(self, config: LRConfig) -> None:
        super().__init__(config)
        self.saved = {}

    def _filename(self):
        return os.path.join(
            self.config.directory,
            hashlib.sha384(self.config.predict.encode()).hexdigest() + '.json'
        )

    async def __aenter__(self) -> LRContext:
        filename = self._filename()
        if os.path.isfile(filename):
            with open(filename, 'r') as read:
                self.saved = json.load(read)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        filename = self._filename()
        with open(filename, 'w') as write:
            json.dump(self.saved, write)

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(
            args,
            above,
            "directory",
            Arg(
                default=os.path.join(
                    os.path.expanduser("~"), ".cache", "dffml", "scikit"
                ),
                help="Directory where state should be saved",
            ),
        )
        cls.config_set(
            args,
            above,
            "predict",
            Arg(
                type=str,
                help="Label or the value to be predicted",
            ),
        )

    @classmethod
    def config(cls, config, *above) -> "LRConfig":
        return LRConfig(
            directory=cls.config_get(config, above, "directory"),
            predict=cls.config_get(config, above, "predict"),
        )
