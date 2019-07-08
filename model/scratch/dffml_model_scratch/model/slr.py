# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Description of what this model does
'''
import os
import abc
import hashlib
import json
from typing import AsyncIterator, Tuple, Any, List, Optional, NamedTuple, Dict
from statistics import mean
import numpy as np

from dffml.repo import Repo
from dffml.source.source import Sources
from dffml.feature import Features
from dffml.accuracy import Accuracy
from dffml.model.model import ModelConfig, ModelContext, Model
from dffml.util.entrypoint import entry_point
from dffml.util.cli.arg import Arg


class SLRConfig(ModelConfig, NamedTuple):
    predict: str
    directory: str  


class SLRContext(ModelContext):

    def __init__(self, parent, features):
        super().__init__(parent, features)
        self.xData = np.array([])
        self.yData = np.array([])
        self.features = self.applicable_features(features)

    def get_regression_line(self):
        return self.parent.saved.get(hashlib.sha384((''.join(sorted(self.features))).encode()).hexdigest(), None)

    def set_regression_line(self, slope, constant, accuracy):
        self.parent.saved[hashlib.sha384((''.join(sorted(self.features))).encode()).hexdigest()] = (slope, constant, accuracy)

    def applicable_features(self, featuress):
        usable = []
        if len(featuress) != 1:
            raise ValueError("Simple Linear Regression doesn't support features other than 1")
        for feature in featuress:
            if feature.dtype() != int and feature.dtype() != float:
                raise ValueError("Simple Linear Regression only supports int or float feature")
            if feature.length() != 1:
                raise ValueError("Simple LR only supports single values (non-matrix / array)")
            usable.append(feature.NAME)
        return usable

    async def predict_input(self, x):
        regression_line = self.get_regression_line()
        prediction = regression_line[0]*x+regression_line[1]
        return prediction

    async def squared_error(self, ys, yline):
        return sum((ys - yline)**2)

    async def coeff_of_deter(self, ys, regression_line):
        y_mean_line = [mean(ys) for y in ys]
        squared_error_mean = await self.squared_error(ys, y_mean_line)
        squared_error_regression = await self.squared_error(ys, regression_line)
        return 1 - (squared_error_regression/squared_error_mean)

    async def best_fit_line(self):
        x = self.xData
        y = self.yData
        mean_x = np.mean(self.xData)
        mean_y = np.mean(self.yData)
        m = (mean_x*mean_y - np.mean(x*y))/((mean_x**2) - np.mean(x*x))
        b = mean_y - (m*mean_x)
        regression_line = [m*x + b for x in x]
        accuracy = await self.coeff_of_deter(y, regression_line)
        self.set_regression_line(m, b, accuracy)
        return (m, b, accuracy)

    async def train(self, sources: Sources):
        async for repo in sources.with_features(self.features):
            feature_data = repo.features(self.features
                                         + [self.parent.config.predict])
            self.xData = np.append(self.xData, feature_data[self.features[0]])
            self.yData = np.append(self.yData, feature_data[self.parent.config.predict])
        self.regression_line = await self.best_fit_line()

    async def accuracy(self, sources: Sources) -> Accuracy:
        regression_line = self.get_regression_line()
        if self.regression_line is None:
            raise ValueError('Model Not Trained')
        accuracy_value = regression_line[2]
        return Accuracy(accuracy_value)

    async def predict(self, repos: AsyncIterator[Repo]) -> \
                    AsyncIterator[Tuple[Repo, Any, float]]:
        regression_line = [await self.predict_input(i) for i in self.xData]
        regression_line = self.get_regression_line()
        async for repo in repos:
            feature_data = repo.features(self.features)
            yield repo, await self.predict_input(feature_data[self.features[0]]), regression_line[2]


@entry_point('slr')
class SLR(Model):

    CONTEXT = SLRContext
    def __init__(self, config: SLRConfig) -> None:
        super().__init__(config)
        self.saved = {}

    def _filename(self):
        return os.path.join(self.config.directory, hashlib.sha384(self.config.predict.encode()).hexdigest() + '.json')

    async def __aenter__(self) -> SLRContext:
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
        cls.config_set(args, above, 'directory', Arg(
            default=os.path.join(os.path.expanduser('~'), '.cache', 'dffml',
                                 'scratch')))
        cls.config_set(args, above, 'predict', Arg(type=str))
        return args

    @classmethod
    def config(cls, config, *above) -> 'SLRConfig':
        return SLRConfig(
            directory=cls.config_get(config, above, 'directory'),
            predict=cls.config_get(config, above, 'predict'),
        )
