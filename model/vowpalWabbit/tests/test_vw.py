import sys
import random
import tempfile

import numpy as np
from sklearn.datasets import make_friedman1

from dffml.repo import Repo
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
                        "X": X[i],
                    }
                },
            )
            for i in range(0, len(A))
        ]

        cls.sources = Sources(
            MemorySource(MemorySourceConfig(repos=cls.repos))
        )
        cls.model = VWModel(
            VWConfig(
                # directory= cls.model_dir.name,
                features=cls.features,
                predict=DefFeature("X", float, 1),
                namespace=["n1_A_B", "n2_A_C"],
                importance="H",
                tag="G",
                convert_to_vw=True,
                passes=50,
                vwcmd="--l2 0.05 --loss_function squared --quiet",
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
                # TODO tune model and set accuracy
                self.assertTrue(isinstance(res, float))

    async def test_02_predict(self):
        async with self.sources as sources, self.model as model:
            target = model.config.predict.NAME
            async with sources() as sctx, model() as mctx:
                async for repo in mctx.predict(sctx.repos()):
                    prediction = repo.prediction(target).value
                    # TODO tune model and set error tolerance
                    self.assertTrue(isinstance(prediction, float))


DATA_LEN = 200
# TODO use text as feature
nouns = ("dog", "cat", "rabbit", "zombie", "monkey")
verbs = ("plays", "eats", "drinks", "runs", "barfs")
adv = ("fancy", "gently", "lively", "merrily.", "occasionally.")
adj = ("adorable", "cool", "silly", "stupid", "smart")
sentences = []
for i in range(DATA_LEN):
    sentences.append(
        random.choice(adj)
        + " "
        + random.choice(nouns)
        + " "
        + random.choice(verbs)
        + " "
        + random.choice(adv)
    )

tag_col = np.arange(1, DATA_LEN + 1)
importance_col = np.random.randint(low=1, high=4, size=DATA_LEN)
X, y = make_friedman1(
    n_samples=DATA_LEN, n_features=6, random_state=2021, noise=3
)

DATA = np.concatenate(
    (X, tag_col[:, None], importance_col[:, None], y[:, None]), axis=1
)
