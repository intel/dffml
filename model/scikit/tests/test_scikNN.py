import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.model.model import ModelConfig
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, DefFeature, Features
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_scikit.scikNN import kNN
from dffml_model_scikit.scikitbase import ScikitConfig


FEATURE_DATA = [
[5,1,1,1,2,1,3,1,1,2],
[5,4,4,5,7,10,3,2,1,2],
[3,1,1,1,2,2,3,1,1,2],
[6,8,8,1,3,4,3,7,1,2],
[4,1,1,3,2,1,3,1,1,2],
[8,10,10,8,7,10,9,7,1,4],
[1,1,1,1,2,10,3,1,1,2],
[2,1,2,1,2,1,3,1,1,2],
[2,1,1,1,2,1,1,1,5,2],
[4,2,1,1,2,1,2,1,1,2],
[1,1,1,1,1,1,3,1,1,2],
[2,1,1,1,2,1,2,1,1,2],
[5,3,3,3,2,3,4,4,1,4],
[1,1,1,1,2,3,3,1,1,2],
[8,7,5,10,7,9,5,5,4,4],
[7,4,6,4,6,1,4,3,1,4],
[4,1,1,1,2,1,2,1,1,2],
[4,1,1,1,2,1,3,1,1,2],
[10,7,7,6,4,10,4,1,2,4],
[6,1,1,1,2,1,3,1,1,2],
[7,3,2,10,5,10,5,4,4,4],
[10,5,5,3,6,7,7,10,1,4],
[2,3,1,1,2,1,2,1,1,2],
[2,1,1,1,1,1,2,1,1,2],
[4,1,3,1,2,1,2,1,1,2],
[3,1,1,1,2,1,2,1,1,2],
[4,1,1,1,2,1,2,1,1,2],
[5,1,1,1,2,1,2,1,1,2],
[3,1,1,1,2,1,2,1,1,2],
[6,3,3,3,3,2,6,1,1,2],
[7,1,2,3,2,1,2,1,1,2],
[1,1,1,1,2,1,1,1,1,2],
[5,1,1,2,1,1,2,1,1,2],
[3,1,3,1,3,4,1,1,1,2],
[4,6,6,5,7,6,7,7,3,4],
[2,1,1,1,2,5,1,1,1,2],
[2,1,1,1,2,1,1,1,1,2],
[4,1,1,1,2,1,1,1,1,2],
[6,2,3,1,2,1,1,1,1,2],
[5,1,1,1,2,1,2,1,1,2],
[1,1,1,1,2,1,1,1,1,2],
]


class TestLR(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = kNN(ScikitConfig(directory=cls.model_dir.name, predict='X'))
        cls.features = Features()

        cls.features.append(DefFeature('A', float, 1))
        cls.features.append(DefFeature('B', float, 1))
        cls.features.append(DefFeature('C', float, 1))
        cls.features.append(DefFeature('D', float, 1))
        cls.features.append(DefFeature('E', float, 1))
        cls.features.append(DefFeature('F', float, 1))
        cls.features.append(DefFeature('G', float, 1))
        cls.features.append(DefFeature('H', float, 1))
        cls.features.append(DefFeature('I', float, 1))
        A, B, C, D, E, F, G, H, I, X = list(zip(*FEATURE_DATA))
        cls.repos = [
            Repo(str(i),
                 data={'features': {
                     'A': A[i],
                     'B': B[i],
                     'C': C[i],
                     'D': D[i],
                     'E': E[i],
                     'F': F[i],
                     'G': G[i],
                     'H': H[i],
                     'I': I[i],
                     'X': X[i],
                     }}
                 )
            for i in range(0, len(A))
            ]
        cls.sources = \
            Sources(MemorySource(MemorySourceConfig(repos=cls.repos)))

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                res = await mctx.accuracy(sctx)
                self.assertTrue(0.0 <= res <= 1.0)

    async def test_02_predict(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                async for repo, prediction, confidence in mctx.predict(sctx.repos()):
                    correct = FEATURE_DATA[int(repo.src_url)][9]
                    self.assertIn(prediction, [2, 4])