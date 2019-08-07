# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
from sklearn.linear_model import LinearRegression

from dffml.util.entrypoint import entry_point
from dffml_model_scikit.scikitbase import Scikit, ScikitContext


class LRContext(ScikitContext):

    def applicable_features(self, features):
        usable = []
        for feature in features:
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

@entry_point("scikitlr")
class LR(Scikit):

    CONTEXT = LRContext
    SCIKIT_MODEL = LinearRegression(n_jobs=-1)
