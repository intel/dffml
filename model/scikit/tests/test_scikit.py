import sys
import tempfile
import numpy as np

from dffml.record import Record
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import DefFeature, Features
from dffml.util.asynctestcase import AsyncTestCase

import dffml_model_scikit.scikit_models
from sklearn.datasets import make_blobs


class TestScikitModel:
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.features = Features()
        if cls.MODEL_TYPE is "CLASSIFICATION":
            cls.features.append(DefFeature("A", float, 1))
            cls.features.append(DefFeature("B", float, 1))
            cls.features.append(DefFeature("C", float, 1))
            cls.features.append(DefFeature("D", float, 1))
            cls.features.append(DefFeature("E", float, 1))
            cls.features.append(DefFeature("F", float, 1))
            cls.features.append(DefFeature("G", float, 1))
            cls.features.append(DefFeature("H", float, 1))
            cls.features.append(DefFeature("I", float, 1))
            A, B, C, D, E, F, G, H, I, X = list(
                zip(*FEATURE_DATA_CLASSIFICATION)
            )
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
                            "I": I[i],
                            "X": X[i],
                        }
                    },
                )
                for i in range(0, len(A))
            ]
        elif cls.MODEL_TYPE is "REGRESSION":
            cls.features.append(DefFeature("A", float, 1))
            cls.features.append(DefFeature("B", float, 1))
            cls.features.append(DefFeature("C", float, 1))
            A, B, C, X = list(zip(*FEATURE_DATA_REGRESSION))
            cls.records = [
                Record(
                    str(i),
                    data={
                        "features": {
                            "A": A[i],
                            "B": B[i],
                            "C": C[i],
                            "X": X[i],
                        }
                    },
                )
                for i in range(0, len(A))
            ]
        elif cls.MODEL_TYPE is "CLUSTERING":
            cls.features.append(DefFeature("A", float, 1))
            cls.features.append(DefFeature("B", float, 1))
            cls.features.append(DefFeature("C", float, 1))
            cls.features.append(DefFeature("D", float, 1))
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
            "directory": cls.model_dir.name,
            "features": cls.features,
        }
        config_fields = dict()
        estimator_type = cls.MODEL.SCIKIT_MODEL._estimator_type
        if estimator_type in supervised_estimators:
            config_fields["predict"] = DefFeature("X", float, 1)
        elif estimator_type in unsupervised_estimators:
            if cls.TRUE_CLSTR_PRESENT:
                config_fields["tcluster"] = DefFeature("X", float, 1)
        cls.model = cls.MODEL(
            cls.MODEL_CONFIG(**{**properties, **config_fields})
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                res = await mctx.accuracy(sctx)
                if self.MODEL_TYPE is "CLUSTERING":
                    self.assertTrue(res is not None)
                else:
                    self.assertTrue(0 <= res <= 1)

    async def test_02_predict(self):
        async with self.sources as sources, self.model as model:
            target = model.config.predict.NAME
            async with sources() as sctx, model() as mctx:
                async for record in mctx.predict(sctx.records()):
                    prediction = record.prediction(target).value
                    if self.MODEL_TYPE is "CLASSIFICATION":
                        self.assertIn(prediction, [2, 4])
                    elif self.MODEL_TYPE is "REGRESSION":
                        correct = FEATURE_DATA_REGRESSION[int(record.key)][3]
                        self.assertGreater(
                            prediction, correct - (correct * 0.40)
                        )
                        self.assertLess(prediction, correct + (correct * 0.40))
                    elif self.MODEL_TYPE is "CLUSTERING":
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
    [2, 1, 1, 1, 2, 1, 1, 1, 5, 2],
    [4, 2, 1, 1, 2, 1, 2, 1, 1, 2],
    [1, 1, 1, 1, 1, 1, 3, 1, 1, 2],
    [2, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [5, 3, 3, 3, 2, 3, 4, 4, 1, 4],
    [1, 1, 1, 1, 2, 3, 3, 1, 1, 2],
    [8, 7, 5, 10, 7, 9, 5, 5, 4, 4],
    [7, 4, 6, 4, 6, 1, 4, 3, 1, 4],
    [4, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [4, 1, 1, 1, 2, 1, 3, 1, 1, 2],
    [10, 7, 7, 6, 4, 10, 4, 1, 2, 4],
    [6, 1, 1, 1, 2, 1, 3, 1, 1, 2],
    [7, 3, 2, 10, 5, 10, 5, 4, 4, 4],
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
    [4, 6, 6, 5, 7, 6, 7, 7, 3, 4],
    [2, 1, 1, 1, 2, 5, 1, 1, 1, 2],
    [2, 1, 1, 1, 2, 1, 1, 1, 1, 2],
    [4, 1, 1, 1, 2, 1, 1, 1, 1, 2],
    [6, 2, 3, 1, 2, 1, 1, 1, 1, 2],
    [5, 1, 1, 1, 2, 1, 2, 1, 1, 2],
    [1, 1, 1, 1, 2, 1, 1, 1, 1, 2],
]

FEATURE_DATA_REGRESSION = [
    [12.39999962, 11.19999981, 1.1, 42393.0],
    [14.30000019, 12.5, 1.3, 49255.0],
    [14.5, 12.69999981, 1.5, 40781.0],
    [14.89999962, 13.10000038, 2.0, 46575.0],
    [16.10000038, 14.10000038, 2.2, 42941.0],
    [16.89999962, 14.80000019, 2.9, 59692.0],
    [16.5, 14.39999962, 3.0, 63200.0],
    [15.39999962, 13.39999962, 3.2, 57495.0],
    [17, 14.89999962, 3.7, 60239.0],
    [17.89999962, 15.60000038, 3.9, 66268.0],
    [18.79999924, 16.39999962, 4.0, 58844.0],
    [20.29999924, 17.70000076, 4.1, 60131.0],
    [22.39999962, 19.60000038, 4.5, 64161.0],
    [19.39999962, 16.89999962, 4.9, 70988.0],
    [15.5, 14, 5.1, 69079.0],
    [16.70000076, 14.60000038, 5.3, 86138.0],
    [17.29999924, 15.10000038, 5.9, 84413.0],
    [18.39999962, 16.10000038, 6.0, 96990.0],
    [19.20000076, 16.79999924, 6.8, 94788.0],
    [17.39999962, 15.19999981, 7.1, 101323.0],
    [19.5, 17, 7.9, 104352.0],
    [19.70000076, 17.20000076, 8.2, 116862.0],
    [21.20000076, 18.60000038, 8.7, 112481.0],
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
valid_estimators = supervised_estimators + unsupervised_estimators
for clf in CLASSIFIERS:
    test_cls = type(
        f"Test{clf}Model",
        (TestScikitModel, AsyncTestCase),
        {
            "MODEL_TYPE": "CLASSIFICATION",
            "MODEL": getattr(dffml_model_scikit.scikit_models, clf + "Model"),
            "MODEL_CONFIG": getattr(
                dffml_model_scikit.scikit_models, clf + "ModelConfig"
            ),
        },
    )
    setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)

for reg in REGRESSORS:
    test_cls = type(
        f"Test{reg}Model",
        (TestScikitModel, AsyncTestCase),
        {
            "MODEL_TYPE": "REGRESSION",
            "MODEL": getattr(dffml_model_scikit.scikit_models, reg + "Model"),
            "MODEL_CONFIG": getattr(
                dffml_model_scikit.scikit_models, reg + "ModelConfig"
            ),
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
            },
        )
        setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)
