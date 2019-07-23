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
    [12.39999962,11.19999981,1.1, 42393.0],
    [14.30000019,12.5,1.3, 49255.0],
    [14.5,12.69999981,1.5, 40781.0],
    [14.89999962,13.10000038,2.0, 46575.0],
    [16.10000038,14.10000038,2.2, 42941.0],
    [16.89999962,14.80000019,2.9, 59692.0],
    [16.5,14.39999962,3.0, 63200.0],
    [15.39999962,13.39999962,3.2, 57495.0],
    [17,14.89999962,3.7, 60239.0],
    [17.89999962,15.60000038,3.9, 66268.0],
    [18.79999924,16.39999962,4.0, 58844.0],
    [20.29999924,17.70000076,4.1, 60131.0],
    [22.39999962,19.60000038,4.5, 64161.0],
    [19.39999962,16.89999962,4.9, 70988.0],
    [15.5,14,5.1, 69079.0],
    [16.70000076,14.60000038,5.3, 86138.0],
    [17.29999924,15.10000038,5.9, 84413.0],
    [18.39999962,16.10000038,6.0, 96990.0],
    [19.20000076,16.79999924,6.8, 94788.0],
    [17.39999962,15.19999981,7.1, 101323.0],
    [19.5,17,7.9, 104352.0],
    [19.70000076,17.20000076,8.2, 116862.0],
    [21.20000076,18.60000038,8.7, 112481.0],
]


class TestLR(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = LR(LRConfig(directory=cls.model_dir.name, predict='Z'))
        cls.features = Features()
        cls.features.append(DefFeature('X', float, 1))
        cls.features.append(DefFeature('Y', float, 1))
        cls.features.append(DefFeature('W', float, 1))
        X, Y, W, Z = list(zip(*FEATURE_DATA))
        cls.repos = [
            Repo(str(i),
                 data={'features': {
                     'X': X[i],
                     'Y': Y[i],
                     'W': W[i],
                     'Z': Z[i]
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
                self.assertTrue(0.0 <= res <= 1.0)
                # Test predict
                async for repo, prediction, confidence in mctx.predict(sctx.repos()):
                    correct = FEATURE_DATA[int(repo.src_url)][3]
                    # Comparison of correct to prediction to make sure prediction is within a reasonable range
                    self.assertGreater(prediction, correct - (correct * 0.20))
                    self.assertLess(prediction, correct + (correct * 0.20))

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
                    correct = FEATURE_DATA[int(repo.src_url)][3]
                    self.assertGreater(prediction, correct - (correct * 0.20))
                    self.assertLess(prediction, correct + (correct * 0.20)) 