# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import abc
import json
import hashlib
from pathlib import Path
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
        self._features_hash = self._feature_predict_hash()
        self.clf = None

    @property
    def confidence(self):
        return self.parent.saved.get(self._features_hash, None)

    @confidence.setter
    def confidence(self, confidence):
        self.parent.saved[self._features_hash] = confidence

    def _feature_predict_hash(self):
        return hashlib.sha384(
            "".join(self.features + [self.parent.config.predict]).encode()
        ).hexdigest()

    def _filename(self):
        return os.path.join(
            self.parent.config.directory,
            self._features_hash + ".joblib",
        )

    async def __aenter__(self):
        if os.path.isfile(self._filename()):
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
                raise ValueError(
                    "Linear Regression only supports int or float feature"
                )
            if feature.length() != 1:
                raise ValueError(
                    "Linear Regression only supports single values (non-matrix / array)"
                )
            usable.append(feature.NAME)
        return sorted(usable)

    async def train(self, sources: Sources):
        data = []
        async for repo in sources.with_features(self.features):
            feature_data = repo.features(
                self.features + [self.parent.config.predict]
            )
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = np.array(df.drop([self.parent.config.predict], 1))
        ydata = np.array(df[self.parent.config.predict])
        self.logger.info("Number of input repos: {}".format(len(xdata)))
        self.clf.fit(xdata, ydata)
        joblib.dump(self.clf, self._filename())

    async def accuracy(self, sources: Sources) -> Accuracy:
        data = []
        async for repo in sources.with_features(self.features):
            feature_data = repo.features(
                self.features + [self.parent.config.predict]
            )
            data.append(feature_data)
        df = pd.DataFrame(data)
        xdata = np.array(df.drop([self.parent.config.predict], 1))
        ydata = np.array(df[self.parent.config.predict])
        self.logger.debug("Number of input repos: {}".format(len(xdata)))
        self.confidence = self.clf.score(xdata, ydata)
        return self.confidence

    async def predict(
        self, repos: AsyncIterator[Repo]
    ) -> AsyncIterator[Tuple[Repo, Any, float]]:
        if self.confidence is None:
            raise ValueError("Model Not Trained")
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
            yield repo, self.clf.predict(predict)[0], self.confidence


@entry_point("scikitlr")
class LR(Model):
    """
    Linear Regression Model implemented using scikit. Models are saved under the
    ``directory`` in subdirectories named after the hash of their feature names.

    .. code-block:: console

        $ cat > train.csv << EOF
        Years,Expertise,Trust,Salary
        0,1,0.2,10
        1,3,0.4,20
        2,5,0.6,30
        3,7,0.8,40
        EOF
        $ cat > test.csv << EOF
        Years,Expertise,Trust,Salary
        4,9,1.0,50
        5,11,1.2,60
        EOF
        $ dffml train \\
            -model scikitlr \\
            -features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \\
            -model-predict Salary \\
            -sources f=csv \\
            -source-filename train.csv \\
            -source-readonly \\
            -log debug
        $ dffml accuracy \\
            -model scikitlr \\
            -features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \\
            -model-predict Salary \\
            -sources f=csv \\
            -source-filename test.csv \\
            -source-readonly \\
            -log debug
        1.0
        $ echo -e 'Years,Expertise,Trust\\n6,13,1.4\\n' | \\
          dffml predict all \\
            -model scikitlr \\
            -features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1 \\
            -model-predict Salary \\
            -sources f=csv \\
            -source-filename /dev/stdin \\
            -source-readonly \\
            -log debug
        [
            {
                "extra": {},
                "features": {
                    "Expertise": 13,
                    "Trust": 1.4,
                    "Years": 6
                },
                "last_updated": "2019-07-31T08:40:59Z",
                "prediction": {
                    "confidence": 1.0,
                    "value": 70.0
                },
                "src_url": "0"
            }
        ]

    """

    CONTEXT = LRContext

    def __init__(self, config: LRConfig) -> None:
        super().__init__(config)
        self.saved = {}

    def _filename(self):
        return os.path.join(
            self.config.directory,
            hashlib.sha384(self.config.predict.encode()).hexdigest() + ".json",
        )

    async def __aenter__(self) -> 'LR':
        path = Path(self._filename())
        if path.is_file():
            self.saved = json.loads(path.read_text())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        Path(self._filename()).write_text(json.dumps(self.saved))

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
            Arg(type=str, help="Label or the value to be predicted"),
        )
        return args

    @classmethod
    def config(cls, config, *above) -> "LRConfig":
        return LRConfig(
            directory=cls.config_get(config, above, "directory"),
            predict=cls.config_get(config, above, "predict"),
        )
