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
    '''
    Model wraping scratch API
    '''
    def __init__(self, parent):
        super().__init__(parent)
        self.xData = np.array([])
        self.yData = np.array([])
        self.regression_line = self.get_regression_line()

    def get_regression_line(self):
        if self.parent.saved.get('regression_line') is None:
            return None
        return self.parent.saved.get('regression_line')

    async def set_regression_line(self, slope, constant, accuracy):
        self.parent.saved['regression_line'] = (slope, constant, accuracy)

    async def squared_error(self, ys, yline):
        return sum((ys - yline)**2)

    async def coeff_of_deter(self, ys, regression_line):
        y_mean_line = [mean(ys) for y in ys]
        squared_error_mean = await self.squared_error(ys, y_mean_line)
        squared_error_regression = await self.squared_error(ys, regression_line)
        return 1 - (squared_error_regression/squared_error_mean)

    async def applicable_features(self, features: Features):
        usable = []
        if len(features) != 1:
            raise ValueError("Simple Linear Regression doesn't support features other than 1")
        for feature in features:
            if feature.dtype() != int and feature.dtype() != float:
                raise ValueError("Simple Linear Regression only supports int or float feature")
            if feature.length() != 1:
                raise ValueError("Simple LR only supports single values (non-matrix / array)")
            usable.append(feature.NAME)
        return usable

    async def best_fit_line(self, xs, ys):
        m = ((mean(xs)*mean(ys)) - mean(xs*ys))/((mean(xs)*mean(xs)) - (mean(xs*xs)))
        b = mean(ys) - (m*mean(xs))
        regression_line = [m*x + b for x in xs]
        accuracy = await self.coeff_of_deter(ys, regression_line)
        await self.set_regression_line(m, b, accuracy)
        return (m, b, accuracy)

    async def predict_input(self, x):
        prediction = self.regression_line[0]*x+self.regression_line[1]
        return prediction

    async def train(self, sources: Sources, features: Features):
        '''
        Train using repos as the data to learn from.
        '''
        feature = await self.applicable_features(features)
        async for repo in sources.with_features(feature):
            # Grab a subset of the feature data being stored within the repo
            # The subset is the feature_we_care_about and the feature we are want to predict
            feature_data = repo.features(feature + [self.parent.config.predict])
            self.xData = np.append(self.xData, feature_data[feature[0]])
            self.yData = np.append(self.yData, feature_data[self.parent.config.predict])
        self.regression_line = await self.best_fit_line(self.xData, self.yData)
        
    async def accuracy(self, sources: Sources, features: Features) -> Accuracy:
        '''
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        '''
        if self.regression_line is None:
            raise ValueError('Model Not Trained')
        accuracy_value = self.regression_line[2]
        return Accuracy(accuracy_value)

    async def predict(self, repos: AsyncIterator[Repo], features: Features) -> \
                    AsyncIterator[Tuple[Repo, Any, float]]:
        '''
        Uses trained data to make a prediction about the quality of a repo.
        '''
        feature = await self.applicable_features(features)
        async for repo in repos:
            feature_data = repo.features(feature)
            yield repo, await self.predict_input(feature_data[feature[0]]), self.regression_line[2]


@entry_point('slr')
class SLR(Model):

    CONTEXT = SLRContext
    
    def __init__(self, config: SLRConfig) -> None:
        super().__init__(config)
        self.saved = {'regression_line': None}

    def _filename(self):
        # Create a file path that is specific to the data we are predicting on
        return os.path.join(self.config.directory, hashlib.sha384(self.config.predict.encode()).hexdigest() + '.json')

    async def __aenter__(self) -> 'SLRContext':
        filename = self._filename()
        if os.path.isfile(filename):
            with open(filename) as read:
                self.saved = json.load(read)
        return self
        # Load from file using open, and json.load. You'll want to make a self.saved property (in __init__ or something)

    async def __aexit__(self, exc_type, exc_value, traceback):
        # Save to the file using open, and json.dump. Dump out the self.saved property to the file.
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
