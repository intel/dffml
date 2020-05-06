import sys
import random
import tempfile

import numpy as np
from sklearn.datasets import make_friedman1

from dffml.record import Record
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import DefFeature, Features
from dffml.util.asynctestcase import AsyncTestCase
from dffml_model_vowpalWabbit.vw_base import VWModel, VWConfig


class TestVWModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.features = Features()
        cls.features.append(DefFeature("A", float, 1))
        cls.features.append(DefFeature("B", float, 1))
        cls.features.append(DefFeature("C", float, 1))
        cls.features.append(DefFeature("D", float, 1))
        cls.features.append(DefFeature("E", float, 1))
        cls.features.append(DefFeature("F", float, 1))
        cls.features.append(DefFeature("G", int, 1))
        cls.features.append(DefFeature("H", int, 1))

        A, B, C, D, E, F, G, H, X = list(zip(*DATA))
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
                    }
                },
            )
            for i in range(0, len(A))
        ]

        cls.sources = Sources(
            MemorySource(MemorySourceConfig(records=cls.records))
        )
        cls.model = VWModel(
            VWConfig(
                directory=cls.model_dir.name,
                features=cls.features,
                predict=DefFeature("X", float, 1),
                # A and B will be namespace n1
                # A and C will be in namespace n2
                namespace=["n1_A_B", "n2_A_C"],
                importance=DefFeature("H", int, 1),
                tag=DefFeature("G", int, 1),
                task="regression",
                convert_to_vw=True,
                vwcmd=[
                    "l2",
                    "0.1",
                    "loss_function",
                    "squared",
                    "passes",
                    "10",
                ],
            )
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
                self.assertTrue(isinstance(res, float))

    async def test_02_predict(self):
        async with self.sources as sources, self.model as model:
            target = model.config.predict.NAME
            async with sources() as sctx, model() as mctx:
                async for record in mctx.predict(sctx.records()):
                    prediction = record.prediction(target).value
                    self.assertTrue(isinstance(prediction, float))


DATA_LEN = 500
tag_col = np.arange(1, DATA_LEN + 1)
importance_col = np.random.randint(low=1, high=4, size=DATA_LEN)
X, y = make_friedman1(
    n_samples=DATA_LEN, n_features=6, random_state=2021, noise=5
)

DATA = np.concatenate(
    (X, tag_col[:, None], importance_col[:, None], y[:, None]), axis=1
)
