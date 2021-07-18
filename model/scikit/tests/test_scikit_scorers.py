import sys

from dffml.high_level.ml import accuracy
from dffml.util.asynctestcase import AsyncTestCase

import dffml_model_scikit.scikit_models

from .test_scikit import (
    REGRESSORS,
    CLUSTERERS,
    CLASSIFIERS,
    TestScikitModel,
    supervised_estimators,
    unsupervised_estimators,
    FEATURE_DATA_REGRESSION,
    FEATURE_DATA_CLUSTERING,
    FEATURE_DATA_CLASSIFICATION,
)


class TestScikitScorer(TestScikitModel):
    async def test_01_accuracy(self):
        res = await accuracy(self.model, self.scorer, self.sources)
        self.assertTrue(float("-inf") < res < float("inf"))

    async def test_02_predict(self):
        pass


REGRESSION_SCORERS = [
    "ExplainedVarianceScore",
    "MaxError",
    "MeanAbsoluteError",
    "MeanSquaredError",
    "MeanSquaredLogError",
    "MedianAbsoluteError",
    "R2Score",
    "MeanPoissonDeviance",
    "MeanGammaDeviance",
    "MeanAbsolutePercentageError",
]

CLASSIFICATION_SCORERS = [
    "AccuracyScore",
    "BalancedAccuracyScore",
    "TopKAccuracyScore",
    "AveragePrecisionScore",
    "F1Score",
    "LogLoss",
    "PrecisionScore",
    "RecallScore",
    "JaccardScore",
]

CLUSTERING_SCORERS = [
    "AdjustedMutualInfoScore",
    "AdjustedRandScore",
    "CompletenessScore",
    "FowlkesMallowsScore",
    "HomogeneityScore",
    "MutualInfoScore",
    "NormalizedMutualInfoScore",
    "RandScore",
    "VMeasureScore",
]


for scorer in REGRESSION_SCORERS:
    for reg in REGRESSORS:
        test_cls = type(
            f"Test{reg}Modelwith{scorer}Scorer",
            (TestScikitScorer, AsyncTestCase),
            {
                "MODEL_TYPE": "REGRESSION",
                "MODEL": getattr(
                    dffml_model_scikit.scikit_models, reg + "Model"
                ),
                "MODEL_CONFIG": getattr(
                    dffml_model_scikit.scikit_models, reg + "ModelConfig"
                ),
                "SCORER": getattr(
                    dffml_model_scikit.scikit_scorers, scorer + "Scorer"
                ),
            },
        )
        setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)

for scorer in CLASSIFICATION_SCORERS:
    for clf in CLASSIFIERS:
        test_cls = type(
            f"Test{clf}Modelwith{scorer}Scorer",
            (TestScikitScorer, AsyncTestCase),
            {
                "MODEL_TYPE": "CLASSIFICATION",
                "MODEL": getattr(
                    dffml_model_scikit.scikit_models, clf + "Model"
                ),
                "MODEL_CONFIG": getattr(
                    dffml_model_scikit.scikit_models, clf + "ModelConfig"
                ),
                "SCORER": getattr(
                    dffml_model_scikit.scikit_scorers, scorer + "Scorer"
                ),
            },
        )
        setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)

for scorer in CLUSTERING_SCORERS:
    for clstr in CLUSTERERS:
        test_cls = type(
            f"Test{clstr}Modelwith{scorer}Scorer",
            (TestScikitScorer, AsyncTestCase),
            {
                "MODEL_TYPE": "CLUSTERING",
                "MODEL": getattr(
                    dffml_model_scikit.scikit_models, clstr + "Model"
                ),
                "MODEL_CONFIG": getattr(
                    dffml_model_scikit.scikit_models, clstr + "ModelConfig"
                ),
                "SCORER": getattr(
                    dffml_model_scikit.scikit_scorers, scorer + "Scorer"
                ),
            },
        )
        setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)
