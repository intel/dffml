import sys
import tempfile

from dffml.repo import Repo
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import DefFeature, Features
from dffml.util.asynctestcase import AsyncTestCase

import dffml_model_scikit.scikit_models


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
            cls.repos = [
                Repo(
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
            cls.repos = [
                Repo(
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
            A, B, C, D = list(zip(*FEATURE_DATA_CLUSTERING))
            cls.repos = [
                Repo(
                    str(i),
                    data={
                        "features": {
                            "A": A[i],
                            "B": B[i],
                            "C": C[i],
                            "D": D[i],
                        }
                    },
                )
                for i in range(0, len(A))
            ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(repos=cls.repos))
        )
        properties = {
            "directory": cls.model_dir.name,
            "features": cls.features,
        }
        predict_field = (
            {"predict": "X"} if cls.MODEL_TYPE not in ["CLUSTERING"] else {}
        )
        cls.model = cls.MODEL(
            cls.MODEL_CONFIG(**{**properties, **predict_field})
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
            async with sources() as sctx, model() as mctx:
                async for repo in mctx.predict(sctx.repos()):
                    prediction = repo.prediction().value
                    if self.MODEL_TYPE is "CLASSIFICATION":
                        self.assertIn(prediction, [2, 4])
                    elif self.MODEL_TYPE is "REGRESSION":
                        correct = FEATURE_DATA_REGRESSION[int(repo.src_url)][3]
                        self.assertGreater(
                            prediction, correct - (correct * 0.40)
                        )
                        self.assertLess(prediction, correct + (correct * 0.40))
                    elif self.MODEL_TYPE is "CLUSTERING":
                        self.assertIn(prediction, [0, 1, 2, 3, 4, 5, 6, 7])


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

FEATURE_DATA_CLUSTERING = [
    [-9.01904123, 6.44409816, 5.95914173, 6.30718146],
    [8.40245806, -2.91001929, 5.52294823, 0.63406374],
    [3.28383325, 9.99244756, -6.71171988, -7.35136935],
    [8.25645943, 5.52158668, -0.83865436, 7.32392625],
    [0.4666179, 3.86571303, 0.80247216, 1.67515402],
    [9.07433439, 7.91270334, 0.17900805, 5.69813477],
    [8.10810537, -1.43034314, 6.3001632, -0.95834529],
    [-9.21920652, 5.55299612, 5.86137319, 8.72662886],
    [-1.46038679, 3.22035416, -1.88257787, 7.47271885],
    [0.71689103, -1.80491159, -3.79870885, 5.801892],
    [1.20875699, -0.88325705, -2.54565181, 6.82120174],
    [-8.92333729, 7.05985875, 4.79321894, 7.93949216],
    [1.2232944, -2.1731803, -5.65333401, 5.0746241],
    [-11.08688964, 7.09178861, 5.72980851, 8.0352744],
    [8.34693133, 6.82753426, -1.7706281, 4.06581243],
    [2.30814319, 8.35692267, -7.96519947, -7.33520733],
    [-10.29019991, 6.50276237, 5.12798147, 9.24950669],
    [8.82761202, 5.15673275, -0.86886528, 4.94710524],
    [-6.77768087, 2.14739483, -8.16717709, 9.57497286],
    [0.08848433, 2.32299086, 1.70735537, 1.05401263],
    [10.69900277, 4.90323978, -1.91788141, 5.17276348],
    [-7.00928003, 1.19636277, -8.23731759, 8.94554342],
    [1.37139124, 10.29780326, -8.45236674, -7.85542464],
    [10.41265589, -3.56599544, 6.2368424, -0.1069117],
    [0.39768362, -2.8748547, -4.1856111, 5.31312746],
    [-8.43792115, 2.10887065, -7.58846676, 8.9108575],
    [10.7615074, -0.43528045, 7.01328033, 0.39797356],
    [0.0677846, -1.94614038, -3.60922816, 6.13993752],
    [-3.14080186, 2.70514198, -2.14372234, 8.22236251],
    [1.07709796, -3.32371724, -4.73321388, 4.74664288],
    [-2.43420238, 2.96982766, -0.51916521, 7.96444293],
    [-10.26996471, 6.68422747, 4.92728894, 8.07667626],
    [11.95551162, 6.92765077, -1.68323498, 6.72759981],
    [-1.34947787, 2.51610133, -2.87845412, 8.29824227],
    [8.20250259, -1.2767179, 5.43132381, 1.80034347],
    [-0.07228289, 2.88376939, 0.34899733, 2.84843906],
    [-7.98850539, 1.42346913, -7.77655265, 6.66997519],
    [2.50904929, 5.7731461, 2.21021495, 1.27582618],
    [2.20656076, 5.50616718, 1.6679407, 0.59536091],
    [0.18776782, 10.45555395, -8.99289782, -9.00486882],
    [9.48153019, -1.35453059, 6.19086716, 1.28447156],
    [-6.44648169, 3.11536304, -6.21207543, 9.21210599],
    [3.24404192, 7.1641737, -9.84976383, -7.2880173],
    [3.2460247, 2.84942165, 2.10102604, 0.71047981],
    [-2.19936446, 2.5583291, -2.06140206, 6.10917741],
    [-8.37407448, 4.34143502, -8.42579116, 9.16042921],
    [-2.03770915, 1.73725008, -1.276438, 8.26379189],
    [0.49966554, 10.42199772, -8.84728221, -7.45495761],
]

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
]

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

for clstr in CLUSTERERS:
    test_cls = type(
        f"Test{clstr}Model",
        (TestScikitModel, AsyncTestCase),
        {
            "MODEL_TYPE": "CLUSTERING",
            "MODEL": getattr(
                dffml_model_scikit.scikit_models, clstr + "Model"
            ),
            "MODEL_CONFIG": getattr(
                dffml_model_scikit.scikit_models, clstr + "ModelConfig"
            ),
        },
    )

    setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)
