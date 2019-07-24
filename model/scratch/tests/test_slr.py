import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.model.model import ModelConfig
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, DefFeature, Features
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_scratch.slr import SLR, SLRConfig


FEATURE_DATA = [
    [12.39999962, 11.19999981],
    [14.30000019, 12.5],
    [14.5, 12.69999981],
    [14.89999962, 13.10000038],
    [16.10000038, 14.10000038],
    [16.89999962, 14.80000019],
    [16.5, 14.39999962],
    [15.39999962, 13.39999962],
    [17, 14.89999962],
    [17.89999962, 15.60000038],
    [18.79999924, 16.39999962],
    [20.29999924, 17.70000076],
    [22.39999962, 19.60000038],
    [19.39999962, 16.89999962],
    [15.5, 14],
    [16.70000076, 14.60000038],
    [17.29999924, 15.10000038],
    [18.39999962, 16.10000038],
    [19.20000076, 16.79999924],
    [17.39999962, 15.19999981],
    [19.5, 17],
    [19.70000076, 17.20000076],
    [21.20000076, 18.60000038],
]


class TestSLR(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = SLR(SLRConfig(directory=cls.model_dir.name, predict="Y"))
        cls.feature = DefFeature("X", float, 1)
        cls.features = Features(cls.feature)
        X, Y = list(zip(*FEATURE_DATA))
        cls.repos = [
            Repo(str(i), data={"features": {"X": X[i], "Y": Y[i]}})
            for i in range(0, len(Y))
        ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(repos=cls.repos))
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_context(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                # Test train
                await mctx.train(sctx)
                # Test accuracy
                res = await mctx.accuracy(sctx)
                self.assertTrue(0.0 <= res < 1.0)
                # Test predict
                async for repo, prediction, confidence in mctx.predict(
                    sctx.repos()
                ):
                    correct = FEATURE_DATA[int(repo.src_url)][1]
                    # Comparison of correct to prediction to make sure prediction is within a reasonable range
                    self.assertGreater(prediction, correct - (correct * 0.10))
                    self.assertLess(prediction, correct + (correct * 0.10))

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
                async for repo, prediction, confidence in mctx.predict(
                    sctx.repos()
                ):
                    correct = FEATURE_DATA[int(repo.src_url)][1]
                    self.assertGreater(prediction, correct - (correct * 0.10))
                    self.assertLess(prediction, correct + (correct * 0.10))
