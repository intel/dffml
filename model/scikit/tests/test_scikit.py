import sys
import tempfile
import numpy as np

from dffml.record import Record
from dffml.high_level.ml import score
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Feature, Features
from dffml.util.asynctestcase import AsyncTestCase

import dffml_model_scikit.scikit_models
from sklearn.datasets import make_blobs
from model.scikit.dffml_model_scikit import (
    SklearnModelAccuracy,
    ScorerWillNotWork,
)


class TestScikitModel:
    @classmethod
    def setUpClass(cls):
        cls.is_multi = "MULTI_" in cls.MODEL_TYPE
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.features = Features()
        if cls.MODEL_TYPE in classifier_types:
            A, B, C, D, E, F, G, H, X, Y = list(
                zip(*FEATURE_DATA_CLASSIFICATION)
            )
            cls.features.append(Feature("A", float, 1))
            cls.features.append(Feature("B", float, 1))
            cls.features.append(Feature("C", float, 1))
            cls.features.append(Feature("D", float, 1))
            cls.features.append(Feature("E", float, 1))
            cls.features.append(Feature("F", float, 1))
            cls.features.append(Feature("G", float, 1))
            cls.features.append(Feature("H", float, 1))
            if cls.MODEL_TYPE == "CLASSIFICATION":
                cls.features.append(Feature("X", float, 1))
            cls.records = [
                Record(
                    str(i),
                    data={
                        "features": {
                            "A": A[i],
                            "B": B[i],
                            "C": C[i],
                            "D": D[i],
                            "E": E[i],
                            "F": F[i],
                            "G": G[i],
                            "H": H[i],
                            "X": X[i],
                            "Y": Y[i],
                        }
                    },
                )
                for i in range(0, len(A))
            ]

        elif cls.MODEL_TYPE in regeressor_types:
            cls.features.append(Feature("A", float, 1))
            cls.features.append(Feature("B", float, 1))
            cls.features.append(Feature("C", float, 1))
            cls.features.append(Feature("D", float, 1))
            if cls.MODEL_TYPE == "REGRESSION":
                cls.features.append(Feature("X", float, 1))
            A, B, C, D, X, Y = list(zip(*FEATURE_DATA_REGRESSION))
            cls.records = [
                Record(
                    str(i),
                    data={
                        "features": {
                            "A": A[i],
                            "B": B[i],
                            "C": C[i],
                            "D": D[i],
                            "X": X[i],
                            "Y": Y[i],
                        }
                    },
                )
                for i in range(0, len(A))
            ]
        elif cls.MODEL_TYPE == "CLUSTERING":
            cls.features.append(Feature("A", float, 1))
            cls.features.append(Feature("B", float, 1))
            cls.features.append(Feature("C", float, 1))
            cls.features.append(Feature("D", float, 1))
            A, B, C, D, X = list(zip(*FEATURE_DATA_CLUSTERING))
            cls.records = [
                Record(
                    str(i),
                    data={
                        "features": {
                            "A": A[i],
                            "B": B[i],
                            "C": C[i],
                            "D": D[i],
                            "X": X[i],
                        }
                    },
                )
                for i in range(0, len(A))
            ]

        cls.sources = Sources(
            MemorySource(MemorySourceConfig(records=cls.records))
        )
        properties = {
            "location": cls.model_dir.name,
            "features": cls.features,
        }
        config_fields = dict()
        estimator_type = cls.MODEL.SCIKIT_MODEL._estimator_type
        if estimator_type in supervised_estimators:
            if cls.is_multi:
                config_fields["predict"] = Features(
                    Feature("X", float, 1), Feature("Y", float, 1)
                )
            else:
                config_fields["predict"] = Feature("X", float, 1)
        elif estimator_type in unsupervised_estimators:
            # TODO If cls.TRUE_CLSTR_PRESENT then we want to use the
            # mutual_info_score scikit accuracy scorer. In this case we might
            # want to change tcluster to a boolean config property.
            # For more info see commit e4f523976bf37d3457cda140ceab7899420ae2c7
            config_fields["predict"] = Feature("X", float, 1)
        cls.model = cls.MODEL(
            cls.MODEL_CONFIG(**{**properties, **config_fields})
        )
        cls.scorer = cls.SCORER()

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        if self.MODEL_TYPE == "CLUSTERING":
            with self.assertRaises(ScorerWillNotWork):
                await score(
                    self.model,
                    self.scorer,
                    self.model.config.predict,
                    self.sources,
                )
        elif self.MODEL_TYPE in regeressor_types:
            res = await score(
                self.model,
                self.scorer,
                self.model.config.predict,
                self.sources,
            )
            self.assertTrue(0 <= res <= float("inf"))
        else:
            res = await score(
                self.model,
                self.scorer,
                self.model.config.predict,
                self.sources,
            )
            self.assertTrue(0 <= res <= 1)

    async def test_02_predict(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                async for record in mctx.predict(sctx):
                    target = (
                        model.config.predict.names()
                        if self.is_multi
                        else model.config.predict.name
                    )
                    if self.is_multi:
                        prediction = [
                            v["value"]
                            for v in record.predictions(target).values()
                        ]
                    else:
                        prediction = record.prediction(target).value
                    if self.MODEL_TYPE == "CLASSIFICATION":
                        self.assertIn(prediction, [2, 4])
                    elif self.MODEL_TYPE == "REGRESSION":
                        correct = FEATURE_DATA_REGRESSION[int(record.key)][3]
                        self.assertGreater(
                            prediction, correct - (correct * 0.40)
                        )
                        self.assertLess(prediction, correct + (correct * 0.40))
                    elif self.MODEL_TYPE == "CLUSTERING":
                        self.assertIn(prediction, [-1, 0, 1, 2, 3, 4, 5, 6, 7])


FEATURE_DATA_CLASSIFICATION = [
    [5, 1, 1, 1, 2, 1, 3, 1, 1, 2],
    [5, 4, 4, 5, 7, 10, 3, 2, 1, 2],
    [3, 1, 1, 1, 2, 2, 3, 1, 1, 2],
    [6, 8, 8, 1, 3, 4, 3, 7, 1, 2],
    [4, 1, 1, 3, 2, 1, 3, 1, 1, 2],
    [8, 10, 10, 8, 7, 10, 9, 7, 1, 4],
    [1, 1, 1, 1, 2, 10, 3, 1, 1, 2],
    [2, 1, 2, 1, 2, 1, 3, 1, 1, 2],
    [2, 1, 1, 1, 2, 1, 1, 1, 2, 2],
    [4, 2, 1, 1, 2, 1, 2, 1, 1, 2],
    [1, 1, 1, 1, 1, 1, 3, 1, 1, 2],
    [2, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [5, 3, 3, 3, 2, 3, 4, 4, 1, 4],
    [1, 1, 1, 1, 2, 3, 3, 1, 1, 2],
    [8, 7, 5, 10, 7, 9, 5, 5, 2, 4],
    [7, 4, 6, 4, 6, 1, 4, 3, 1, 4],
    [4, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [4, 1, 1, 1, 2, 1, 3, 1, 1, 2],
    [10, 7, 7, 6, 4, 10, 4, 1, 2, 4],
    [6, 1, 1, 1, 2, 1, 3, 1, 1, 2],
    [7, 3, 2, 10, 5, 10, 5, 4, 2, 4],
    [10, 5, 5, 3, 6, 7, 7, 10, 1, 4],
    [2, 3, 1, 1, 2, 1, 2, 1, 1, 2],
    [2, 1, 1, 1, 1, 1, 2, 1, 1, 2],
    [4, 1, 3, 1, 2, 1, 2, 1, 1, 2],
    [3, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [4, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [5, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [3, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [6, 3, 3, 3, 3, 2, 6, 1, 1, 2],
    [7, 1, 2, 3, 2, 1, 2, 1, 1, 2],
    [1, 1, 1, 1, 2, 1, 1, 1, 1, 2],
    [5, 1, 1, 2, 1, 1, 2, 1, 1, 2],
    [3, 1, 3, 1, 3, 4, 1, 1, 1, 2],
    [4, 6, 6, 5, 7, 6, 7, 7, 2, 4],
    [2, 1, 1, 1, 2, 5, 1, 1, 1, 2],
    [2, 1, 1, 1, 2, 1, 1, 1, 1, 2],
    [4, 1, 1, 1, 2, 1, 1, 1, 2, 2],
    [6, 2, 3, 1, 2, 1, 1, 1, 1, 2],
    [5, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [1, 1, 1, 1, 2, 1, 1, 1, 2, 2],
]

FEATURE_DATA_REGRESSION = [
    [5.0, 162.0, 60.0, 191.0, 36.0, 50.0],
    [2.0, 110.0, 60.0, 189.0, 37.0, 52.0],
    [12.0, 101.0, 101.0, 193.0, 38.0, 58.0],
    [12.0, 105.0, 37.0, 162.0, 35.0, 62.0],
    [13.0, 155.0, 58.0, 189.0, 35.0, 46.0],
    [4.0, 101.0, 42.0, 182.0, 36.0, 56.0],
    [8.0, 101.0, 38.0, 211.0, 38.0, 56.0],
    [6.0, 125.0, 40.0, 167.0, 34.0, 60.0],
    [15.0, 200.0, 40.0, 176.0, 31.0, 74.0],
    [17.0, 251.0, 250.0, 154.0, 33.0, 56.0],
    [17.0, 120.0, 38.0, 169.0, 34.0, 50.0],
    [13.0, 210.0, 115.0, 166.0, 33.0, 52.0],
    [14.0, 215.0, 105.0, 154.0, 34.0, 64.0],
    [1.0, 50.0, 50.0, 247.0, 46.0, 50.0],
    [6.0, 70.0, 31.0, 193.0, 36.0, 46.0],
    [12.0, 210.0, 120.0, 202.0, 37.0, 62.0],
    [4.0, 60.0, 25.0, 176.0, 37.0, 54.0],
    [11.0, 230.0, 80.0, 157.0, 32.0, 52.0],
    [15.0, 225.0, 73.0, 156.0, 33.0, 54.0],
    [2.0, 110.0, 43.0, 138.0, 33.0, 68.0],
]

"""
FEATURE_DATA_CLUSTERING = [
    [-9.01904123, 6.44409816, 5.95914173, 6.30718146],
    [ 7.10630876, -2.07342124, -0.72564101,  3.81251745],
    ...
    ]
"""
data, labels = make_blobs(
    n_samples=80, centers=8, n_features=4, random_state=2020
)
FEATURE_DATA_CLUSTERING = np.concatenate((data, labels[:, None]), axis=1)
CLASSIFIERS = [
    "KNeighborsClassifier",
    "SVC",
    "GaussianProcessClassifier",
    "DecisionTreeClassifier",
    "RandomForestClassifier",
    "MLPClassifier",
    "AdaBoostClassifier",
    "GaussianNB",
    "QuadraticDiscriminantAnalysis",
    "LogisticRegression",
    "GradientBoostingClassifier",
    "BernoulliNB",
    "ExtraTreesClassifier",
    "BaggingClassifier",
    "LinearDiscriminantAnalysis",
    "MultinomialNB",
]

REGRESSORS = [
    "LinearRegression",
    "ElasticNet",
    "BayesianRidge",
    "Lasso",
    "ARDRegression",
    "RANSACRegressor",
    "DecisionTreeRegressor",
    "GaussianProcessRegressor",
    "OrthogonalMatchingPursuit",
    "Lars",
    "Ridge",
]

CLUSTERERS = [
    "KMeans",
    "Birch",
    "MiniBatchKMeans",
    "AffinityPropagation",
    "MeanShift",
    "SpectralClustering",
    "AgglomerativeClustering",
    "OPTICS",
]

supervised_estimators = ["classifier", "regressor"]
unsupervised_estimators = ["clusterer"]
classifier_types = ["CLASSIFICATION", "MULTI_CLASSIFICATION"]
regeressor_types = ["REGRESSION", "MULTI_REGRESSION"]
valid_estimators = supervised_estimators + unsupervised_estimators

for clf in CLASSIFIERS:
    for model_type in classifier_types:
        test_cls = type(
            f"Test{clf}Model",
            (TestScikitModel, AsyncTestCase),
            {
                "MODEL_TYPE": model_type,
                "MODEL": getattr(
                    dffml_model_scikit.scikit_models, clf + "Model"
                ),
                "MODEL_CONFIG": getattr(
                    dffml_model_scikit.scikit_models, clf + "ModelConfig"
                ),
                "SCORER": SklearnModelAccuracy,
            },
        )
        setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)

for reg in REGRESSORS:
    for model_type in regeressor_types:
        test_cls = type(
            f"Test{reg}Model",
            (TestScikitModel, AsyncTestCase),
            {
                "MODEL_TYPE": model_type,
                "MODEL": getattr(
                    dffml_model_scikit.scikit_models, reg + "Model"
                ),
                "MODEL_CONFIG": getattr(
                    dffml_model_scikit.scikit_models, reg + "ModelConfig"
                ),
                "SCORER": SklearnModelAccuracy,
            },
        )
    setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)


for clstr in CLUSTERERS:
    for true_clstr_present in [True, False]:
        labelInfo = f"withLabel" if true_clstr_present else f"withoutLabel"
        test_cls = type(
            f"Test{clstr}Model" + labelInfo,
            (TestScikitModel, AsyncTestCase),
            {
                "MODEL_TYPE": "CLUSTERING",
                "MODEL": getattr(
                    dffml_model_scikit.scikit_models, clstr + "Model"
                ),
                "MODEL_CONFIG": getattr(
                    dffml_model_scikit.scikit_models, clstr + "ModelConfig"
                ),
                "TRUE_CLSTR_PRESENT": true_clstr_present,
                "SCORER": SklearnModelAccuracy,
            },
        )
        setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)
