import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.model.model import ModelConfig
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, DefFeature, Features
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_scikit.sciLR import LR, LRConfig

FEATURE_DATA = [
    [1.1, 42393.0],
    [1.3, 49255.0],
    [1.5, 40781.0],
    [2.0, 46575.0],
    [2.2, 42941.0],
    [2.9, 59692.0],
    [3.0, 63200.0],
    [3.2, 57495.0],
    [3.2, 67495.0],
    [3.7, 60239.0],
    [3.9, 66268.0],
    [4.0, 58844.0],
    [4.0, 60007.0],
    [4.1, 60131.0],
    [4.5, 64161.0],
    [4.9, 70988.0],
    [5.1, 69079.0],
    [5.3, 86138.0],
    [5.9, 84413.0],
    [6.0, 96990.0],
    [6.8, 94788.0],
    [7.1, 101323.0],
    [7.9, 104352.0],
    [8.2, 116862.0],
    [8.7, 112481.0],
    [9.0, 108632.0],
    [9.5, 120019.0],
    [9.6, 115685.0],
    [10.3, 125441.0],
    [10.5, 124922.0],
]


class TestSLR(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = LR(LRConfig(directory=cls.model_dir.name, predict='Y'))
        cls.feature = DefFeature('X', float, 1)
        cls.features = Features(cls.feature)
        X, Y = list(zip(*FEATURE_DATA))
        cls.repos = [
            Repo(str(i),
                 data={'features': {
                     'X': X[i],
                     'Y': Y[i],
                     }}
                 )
            for i in range(0, len(Y))
            ]
        cls.sources = \
            Sources(MemorySource(MemorySourceConfig(repos=cls.repos)))

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_context(self):
        async with self.sources as sources, self.features as features, \
                self.model as model:
            async with sources() as sctx, model(features) as mctx:
                # Test train
                await mctx.train(sctx)
                # Test accuracy
                res = await mctx.accuracy(sctx)
                print(res)
                self.assertTrue(0.0 <= res < 1.0)
                # Test predict
                async for repo, prediction, confidence in mctx.predict(sctx.repos()):
                    correct = FEATURE_DATA[int(repo.src_url)][1]
                    # Comparison of correct to prediction to make sure prediction is within a reasonable range
                    # self.assertGreater(prediction, correct - (correct * 0.10))
                    # self.assertLess(prediction, correct + (correct * 0.10))

    async def test_00_train(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                res = await mctx.accuracy(sctx)
                self.assertTrue(0.0 <= res < 1.0)

    async def test_02_predict(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                async for repo, prediction, confidence in mctx.predict(sctx.repos()):
                    correct = FEATURE_DATA[int(repo.src_url)][1]
                    self.assertGreater(prediction, correct - (correct * 0.10))
                    self.assertLess(prediction, correct + (correct * 0.10)) 