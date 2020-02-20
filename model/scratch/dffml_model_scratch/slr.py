# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import json
import hashlib
from typing import AsyncIterator, Tuple, Any

import numpy as np

from dffml.repo import Repo
from dffml.base import config, field
from dffml.source.source import Sources
from dffml.model.accuracy import Accuracy
from dffml.model.model import ModelContext, Model, ModelNotTrained
from dffml.util.entrypoint import entrypoint
from dffml.feature.feature import Feature, Features


@config
class SLRConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on")
    directory: str = field(
        "Directory where state should be saved",
        default=os.path.join(
            os.path.expanduser("~"), ".cache", "dffml", "scratch"
        ),
    )


class SLRContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.xData = np.array([])
        self.yData = np.array([])
        self.features = self.applicable_features(self.parent.config.features)
        self._features_hash_ = hashlib.sha384(
            ("".join(sorted(self.features))).encode()
        ).hexdigest()

    @property
    def regression_line(self):
        return self.parent.saved.get(self._features_hash_, None)

    @regression_line.setter
    def regression_line(self, rline):
        self.parent.saved[self._features_hash_] = rline

    def applicable_features(self, features):
        usable = []
        if len(features) != 1:
            raise ValueError(
                "Simple Linear Regression doesn't support features other than 1"
            )
        for feature in features:
            if feature.dtype() != int and feature.dtype() != float:
                raise ValueError(
                    "Simple Linear Regression only supports int or float feature"
                )
            if feature.length() != 1:
                raise ValueError(
                    "Simple LR only supports single values (non-matrix / array)"
                )
            usable.append(feature.NAME)
        return sorted(usable)

    async def predict_input(self, x):
        prediction = self.regression_line[0] * x + self.regression_line[1]
        self.logger.debug(
            "Predicted Value of {} {}:".format(
                self.parent.config.predict.NAME, prediction
            )
        )
        return prediction

    async def squared_error(self, ys, yline):
        return sum((ys - yline) ** 2)

    async def coeff_of_deter(self, ys, regression_line):
        y_mean_line = [np.mean(ys) for y in ys]
        squared_error_mean = await self.squared_error(ys, y_mean_line)
        squared_error_regression = await self.squared_error(
            ys, regression_line
        )
        return 1 - (squared_error_regression / squared_error_mean)

    async def best_fit_line(self):
        self.logger.debug("Number of input repos: {}".format(len(self.xData)))
        x = self.xData
        y = self.yData
        mean_x = np.mean(self.xData)
        mean_y = np.mean(self.yData)
        m = (mean_x * mean_y - np.mean(x * y)) / (
            (mean_x ** 2) - np.mean(x * x)
        )
        b = mean_y - (m * mean_x)
        regression_line = [m * x + b for x in x]
        accuracy = await self.coeff_of_deter(y, regression_line)
        return (m, b, accuracy)

    async def train(self, sources: Sources):
        async for repo in sources.with_features(
            self.features + [self.parent.config.predict.NAME]
        ):
            feature_data = repo.features(
                self.features + [self.parent.config.predict.NAME]
            )
            self.xData = np.append(self.xData, feature_data[self.features[0]])
            self.yData = np.append(
                self.yData, feature_data[self.parent.config.predict.NAME]
            )
        self.regression_line = await self.best_fit_line()

    async def accuracy(self, sources: Sources) -> Accuracy:
        if self.regression_line is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")
        accuracy_value = self.regression_line[2]
        return Accuracy(accuracy_value)

    async def predict(
        self, repos: AsyncIterator[Repo]
    ) -> AsyncIterator[Tuple[Repo, Any, float]]:
        if self.regression_line is None:
            raise ModelNotTrained("Train model before prediction.")
        target = self.parent.config.predict.NAME
        async for repo in repos:
            feature_data = repo.features(self.features)
            repo.predicted(
                target,
                await self.predict_input(feature_data[self.features[0]]),
                self.regression_line[2],
            )
            yield repo


@entrypoint("slr")
class SLR(Model):
    """
    Simple Linear Regression Model for 2 variables implemented from scratch.
    Models are saved under the ``directory`` in subdirectories named after the
    hash of their feature names.

    .. code-block:: console

        $ cat > dataset.csv << EOF
        Years,Salary
        1,40
        2,50
        3,60
        4,70
        5,80
        EOF
        $ dffml train \\
            -model scratchslr \\
            -model-features Years:int:1 \\
            -model-predict Salary:float:1 \\
            -sources f=csv \\
            -source-filename dataset.csv \\
            -log debug
        $ dffml accuracy \\
            -model scratchslr \\
            -model-features Years:int:1 \\
            -model-predict Salary:float:1 \\
            -sources f=csv \\
            -source-filename dataset.csv \\
            -log debug
        1.0
        $ echo -e 'Years,Salary\\n6,0\\n' | \\
          dffml predict all \\
            -model scratchslr \\
            -model-features Years:int:1 \\
            -model-predict Salary:float:1 \\
            -sources f=csv \\
            -source-filename /dev/stdin \\
            -log debug
        [
            {
                "extra": {},
                "features": {
                    "Salary": 0,
                    "Years": 6
                },
                "last_updated": "2019-07-19T09:46:45Z",
                "prediction": {
                    "Salary": {
                        "confidence": 1.0,
                        "value": 90.0
                    }
                },
                "key": "0"
            }
        ]

    """

    CONTEXT = SLRContext
    CONFIG = SLRConfig

    def __init__(self, config: SLRConfig) -> None:
        super().__init__(config)
        self.saved = {}

    def _filename(self):
        return os.path.join(
            self.config.directory,
            hashlib.sha384(self.config.predict.NAME.encode()).hexdigest()
            + ".json",
        )

    async def __aenter__(self) -> SLRContext:
        filename = self._filename()
        if os.path.isfile(filename):
            with open(filename, "r") as read:
                self.saved = json.load(read)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        filename = self._filename()
        with open(filename, "w") as write:
            json.dump(self.saved, write)
