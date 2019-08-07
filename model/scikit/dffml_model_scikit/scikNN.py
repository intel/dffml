# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
from sklearn.neighbors import KNeighborsClassifier

from dffml.util.entrypoint import entry_point
from dffml_model_scikit.scikitbase import Scikit, ScikitContext


class kNNContext(ScikitContext):

    def applicable_features(self, features):
        usable = []
        for feature in features:
            if feature.dtype() != int and feature.dtype() != float:
                raise ValueError(
                    "kNN only supports int or float feature"
                )
            if feature.length() != 1:
                raise ValueError(
                    "kNN only supports single values (non-matrix / array)"
                )
            usable.append(feature.NAME)
        return sorted(usable)

@entry_point("scikitknn")
class kNN(Scikit):

    CONTEXT = kNNContext
    SCIKIT_MODEL = KNeighborsClassifier(n_jobs=-1)