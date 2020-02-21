# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import abc
import json
import hashlib
import numbers
import numpy as np
from typing import AsyncIterator, Tuple, Any, List, Optional, NamedTuple, Dict
from rgrsupport import f_normalize, _ridge_regression
import numpy as np

from dffml.repo import Repo
from dffml.base import config, field
from dffml.source.source import Sources
from dffml.feature import Features
from dffml.model.accuracy import Accuracy
from dffml.model.model import ModelConfig, ModelContext, Model, ModelNotTrained
from dffml.util.entrypoint import entrypoint
from dffml.util.cli.arg import Arg
from dffml.feature.feature import Feature, Features
from dffml.util.cli.parser import list_action


@config
class RidgeConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on")
    directory: str = field(
        "Directory where state should be saved",
        default=os.path.join(
            os.path.expanduser("~"), ".cache", "dffml", "scratch"
        ),
    )


class RidgeContext(ModelContext):
    def __init__(self, parent, alpha=1.0, fit_intercept=True, normalize=False,
                copy_X=True, max_iter=None, tol=1e-3,
                random_state=None):
        super().__init__(parent)
        self.xData = np.array([])
        self.yData = np.array([])
        self.features = self.applicable_features(self.parent.config.features)
        self._features_hash_ = hashlib.sha384(
            ("".join(sorted(self.features))).encode()
        ).hexdigest()
        self.alpha = alpha
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.copy_X = copy_X
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.coef_ = None


    def applicable_features(self, features):
        usable = []
        for feature in features:
            if feature.dtype() != int and feature.dtype() != float:
                raise ValueError(
                    "Ridge Regression only supports int or float feature"
                )
            if feature.length() != 1:
                raise ValueError(
                    "Ridge only supports single values (non-matrix / array)"
                )
            usable.append(feature.NAME)
        return sorted(usable)

    async def predict_input(self, x):
        prediction = np.dot(np.asarray([x], dtype=float), self.coef_.T)  + self.intercept_
        try:
            prediction = prediction[0]
        except:
            pass
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
        await self.fit(self.xData, self.yData)
    
    async def _preprocess_data(self, X, y, fit_intercept, normalize=False, copy=True,
                     sample_weight=None, return_mean=False):

        if isinstance(sample_weight, numbers.Number):
            sample_weight = None
        if copy:
            X = X.copy(order='K')

        y = np.asarray(y, dtype=X.dtype)

        if fit_intercept:
            X_offset = np.average(X, axis=0, weights=sample_weight)
            X -= X_offset
            if normalize:
                X, X_scale = f_normalize(X, axis=0, copy=False,
                                         return_norm=True)
            else:
                X_scale = np.ones(X.shape[1], dtype=X.dtype)
            y_offset = np.average(y, axis=0, weights=sample_weight)
            y = y - y_offset
        else:
            X_offset = np.zeros(X.shape[1], dtype=X.dtype)
            X_scale = np.ones(X.shape[1], dtype=X.dtype)
            if y.ndim == 1:
                y_offset = X.dtype.type(0)
            else:
                y_offset = np.zeros(y.shape[1], dtype=X.dtype)

        return X, y, X_offset, y_offset, X_scale


    async def fit(self, X, y, sample_weight=None):
        X = np.asarray(X)
        y = np.array(y)
        if len(X.shape) < 2:
            X = X.reshape(-1, 1)
        X, y, X_offset, y_offset, X_scale = await self._preprocess_data(
                X, y, self.fit_intercept, self.normalize, self.copy_X,
                sample_weight=sample_weight, return_mean=True)
        params = {}
        self.coef_, self.n_iter_ = await _ridge_regression(
                X, y, alpha=self.alpha, sample_weight=sample_weight,
                max_iter=self.max_iter, tol=self.tol,
                random_state=self.random_state, return_n_iter=True,
                return_intercept=False, check_input=False, **params)
        await self._set_intercept(X_offset, y_offset, X_scale)
        self.accuracy_value = await self.coeff_of_deter(y, \
            np.dot(np.asarray(X, dtype=float), self.coef_.T)  + self.intercept_)
        file_addr = str(os.path.join(self.parent.config.directory, self._features_hash_))
        with open(file_addr + "weights.txt", 'w') as f:
            f.write(",".join(map(str, self.coef_)))
        with open(file_addr + "intercept.txt", 'w') as f:
            f.write(str(self.intercept_))
        with open(file_addr + "acc.txt", 'w') as f:
            f.write(str(self.accuracy_value))
        return self
    
    async def _set_intercept(self, X_offset, y_offset, X_scale):
        """Set the intercept_
        """
        if self.fit_intercept:
            self.coef_ = self.coef_ / X_scale
            self.intercept_ = y_offset - np.dot(X_offset, self.coef_.T)
        else:
            self.intercept_ = 0.

    async def train(self, sources: Sources):
        data = []
        async for repo in sources.with_features(
            self.features + [self.parent.config.predict.NAME]
        ):
            feature_data = repo.features(
                self.features + [self.parent.config.predict.NAME]
            )
            slice_ = [feature_data[data] for data in self.features]
            data.append(slice_)
            self.yData = np.append(
                self.yData, feature_data[self.parent.config.predict.NAME]
            )
        self.xData = np.asarray(data, dtype=float).reshape(-1, len(self.features))
        await self.best_fit_line()

    async def accuracy(self, sources: Sources) -> Accuracy:
        file_addr = str(os.path.join(self.parent.config.directory, self._features_hash_))
        try:
            with open(file_addr + "acc.txt", "r") as f:
                self.accuracy_value = float(f.read())
        except:
            raise ModelNotTrained("Train model before assessing for accuracy.")
        return Accuracy(self.accuracy_value)

    async def predict(
        self, repos: AsyncIterator[Repo]
    ) -> AsyncIterator[Tuple[Repo, Any, float]]:
        try:
            file_addr = str(os.path.join(self.parent.config.directory, self._features_hash_))
            with open(file_addr + "weights.txt", 'r') as f:
                self.coef_ = np.asarray(list(map(float, f.read().split(","))), dtype=float)
            with open(file_addr + "intercept.txt", 'r') as f:
                self.intercept_ = float(f.read())
            with open(file_addr + "acc.txt", 'r') as f:
                self.accuracy_value = float(f.read())
        except:
            raise ModelNotTrained("Train model before prediction.")
        target = self.parent.config.predict.NAME
        async for repo in repos:
            feature_data = repo.features(self.features)
            repo.predicted(
                target,
                await self.predict_input([feature_data[data] for data in self.features]),
                self.accuracy_value,
            )
            yield repo


@entrypoint("ridge")
class RidgeRegression(Model):
    
    CONTEXT = RidgeContext
    CONFIG = RidgeConfig

    def __init__(self, config: RidgeConfig) -> None:
        super().__init__(config)
        self.saved = {}
