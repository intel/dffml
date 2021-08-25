# SPDX-License-Identifier: MIT
# Copyright (c) 2021 Intel Corporation
"""
Base class for Scikit scorers
"""

import numpy as np

from dffml.base import config
from dffml.model.model import ModelContext
from dffml.source.source import SourcesContext
from dffml.accuracy import AccuracyScorer, AccuracyContext
from dffml.feature import Feature
from .scikit_base import NoMultiOutputSupport

MULTIOUTPUT_EXCEPTIONS = [
    "MaxError",
    "MeanGammaDeviance",
    "MeanPoissonDeviance",
]


@config
class ScikitScorerConfig:
    pass


class ScikitScorerContext(AccuracyContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.scorer = None

    async def __aenter__(self):
        self.scorer = self.parent.SCIKIT_SCORER
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def score(
        self, mctx: ModelContext, sctx: SourcesContext, *features: Feature,
    ):
        is_multi = len(features) > 1
        if is_multi:
            for scorer in MULTIOUTPUT_EXCEPTIONS:
                if scorer in str(self.__class__.__qualname__):
                    raise NoMultiOutputSupport(
                        "Scorer does not support Multi-Output. Please refer the docs to find a suitable scorer entrypoint."
                    )
            predictions = [feature.name for feature in features]
        elif len(features) == 1:
            (features,) = features
            predictions = features.name
        y_true = []
        y_pred = []
        async for record in mctx.predict(sctx):
            if is_multi:
                y_true.append(list(record.features(predictions).values()))
                y_pred.append(
                    [
                        pred["value"]
                        for pred in record.predictions(predictions).values()
                    ]
                )
            else:
                y_true.append(record.feature(predictions))
                y_pred.append(record.prediction(predictions).value)
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        return self.scorer(y_true, y_pred, **self.parent.config._asdict())


class ScikitScorer(AccuracyScorer):

    CONFIG = ScikitScorerConfig

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass
