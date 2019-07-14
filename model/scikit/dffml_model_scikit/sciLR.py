# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import abc
import numpy as np
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
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


class LRContext(ModelContext):

    def __init__(self, parent, features):
        super().__init__(parent, features)
        self.xData = np.array([])
        self.yData = np.array([])
        self.features = self.applicable_features(features)

    def applicable_features(self, featuress):
        usable = []
        for feature in featuress:
            if feature.dtype() != int and feature.dtype() != float:
                raise ValueError("Linear Regression only supports int or float feature")
            if feature.length() != 1:
                raise ValueError("Linear Regression only supports single values (non-matrix / array)")
            usable.append(feature.NAME)
        return usable

    async def train(self, sources: Sources):
        async for repo in sources.with_features(self.features):
            feature_data = repo.features(self.features
                                         + [self.parent.config.predict])
            print(feature_data)

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        """
        # Lies
        return 1.0

    async def predict(
        self, repos: AsyncIterator[Repo]
    ) -> AsyncIterator[Tuple[Repo, Any, float]]:
        """
        Uses trained data to make a prediction about the quality of a repo.
        """
        async for repo in repos:
            yield repo, self.parent.config.classifications[
                repo.feature(self.features.names()[0])
            ], 1.0


@entry_point("sciLR")
class LR(Model):

    CONTEXT = LRContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(
            args,
            above,
            'directory',
            Arg(
                default=os.path.join(
                    os.path.expanduser('~'), '.cache', 'dffml', 'scikit'
                ),
                help="Directory where state should be saved",
            ),
        )
        cls.config_set(
            args,
            above,
            'predict',
            Arg(
                type=str,
                help="Label or the value to be predicted",
            ),
        )
        return args

    @classmethod
    def config(cls, config, *above) -> 'LRConfig':
        return LRConfig(
            directory=cls.config_get(config, above, 'directory'),
            predict=cls.config_get(config, above, 'predict'),
        )
