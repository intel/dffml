# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import abc
import hashlib
import numpy as np
import pandas as pd
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.externals import joblib
from typing import AsyncIterator, Tuple, Any, List, Optional, NamedTuple, Dict

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
    # scale: bool


class LRContext(ModelContext):

    def __init__(self, parent, features):
        super().__init__(parent, features)
        self.xData = np.array([])
        self.yData = np.array([])
        self.features = self.applicable_features(features)
        self.confidence = None
        self.clf = None

    def _filename(self):
        return os.path.join(
            self.parent.config.directory,
            hashlib.sha384(self.parent.config.predict.encode()).hexdigest() + '.joblib')

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
        xData = np.array(df.drop([self.parent.config.predict], 1))
        # xData = preprocessing.scale(xData)
        yData = np.array(df[self.parent.config.predict])
        self.clf.fit(xData, yData)
        joblib.dump(self.clf, self._filename())

    async def accuracy(self, sources: Sources) -> Accuracy:
        if(os.path.isfile(self._filename())):
            data = []
            async for repo in sources.with_features(self.features):
                feature_data = repo.features(self.features
                                         + [self.parent.config.predict])
                data.append(feature_data)
            df = pd.DataFrame(data)
            xData = np.array(df.drop([self.parent.config.predict], 1))
            # xData = preprocessing.scale(xData)
            yData = np.array(df[self.parent.config.predict])
            self.confidence = self.clf.score(xData, yData)
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
            yield repo, self.clf.predict(predict), self.confidence


@entry_point("sciLR")
class LR(Model):

    CONTEXT = LRContext

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
        # cls.config_set(
        #     args,
        #     above,
        #     "scale",
        #     Arg(
        #         type=bool,
        #         action="store_true",
        #         help="Enable dataset scaling"
        #     ),
        # )
        # return args

    @classmethod
    def config(cls, config, *above) -> "LRConfig":
        return LRConfig(
            directory=cls.config_get(config, above, "directory"),
            predict=cls.config_get(config, above, "predict"),
            # scale=cls.config_get(config, above, "scale"),
        )
