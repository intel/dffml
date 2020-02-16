import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.model.model import ModelConfig
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, DefFeature, Features
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_scratch.ridge import RidgeRegression, RidgeConfig

Features_data = [
    {"Years": 0, "Salary": 21,  "Expertise": 1, "Trust": 0.1}, 
    {"Years": 1, "Salary": 31, "Expertise": 1, "Trust": 0.1}, 
    {"Years": 2, "Salary": 40, "Expertise": 1, "Trust": 0.1}, 
    {"Years": 3, "Salary": 79, "Expertise": 3, "Trust": 0.2}, 
    {"Years": 4, "Salary": 89, "Expertise": 3, "Trust": 0.2}, 
    {"Years": 5, "Salary": 102, "Expertise": 3, "Trust": 0.2}, 
    {"Years": 6, "Salary": 145, "Expertise": 5, "Trust": 0.3}, 
    {"Years": 7, "Salary": 150, "Expertise": 5, "Trust": 0.3}, 
    {"Years": 8, "Salary": 160, "Expertise": 5, "Trust": 0.3}, 
    {"Years": 9, "Salary": 209, "Expertise": 7, "Trust": 0.4}, 
    {"Years": 10, "Salary": 210, "Expertise": 7, "Trust": 0.4}, 
    {"Years": 11, "Salary": 215, "Expertise": 7, "Trust": 0.4}, 
]

class TestRidge(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.feature1 = DefFeature("Years", float, 1)
        cls.feature2 = DefFeature("Expertise", float, 1)
        cls.feature3 = DefFeature("Trust", float, 1)
        cls.features = ['Expertise', 'Trust', 'Years']
        cls.repos = [
            Repo(str(i), data={"features": Features_data[i]})
            for i in range(0, len(Features_data))
        ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(repos=cls.repos))
        )
        cls.model = RidgeRegression(
            RidgeConfig(
                directory=cls.model_dir.name,
                predict=DefFeature("Salary", float, 1),
                features=cls.features,
            )
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_context(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                # Test train
                await mctx.train(sctx)
                # Test accuracy
                res = await mctx.accuracy(sctx)
                self.assertTrue(0.0 <= res < 1.0)
                # Test predict
                target_name = model.config.predict.NAME
                async for repo in mctx.predict(sctx.repos()):
                    correct = Features_data[int(repo.key)]["Salary"]
                    # Comparison of correct to prediction to make sure prediction is within a reasonable range
                    prediction = repo.prediction(target_name).value
                    self.assertGreater(prediction, correct - (correct * 0.20))
                    self.assertLess(prediction, correct + (correct * 0.20))

    async def test_00_train(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                res = await mctx.accuracy(sctx)
                self.assertTrue(0.0 <= res < 1.0)

    async def test_02_predict(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                target_name = model.config.predict.NAME
                async for repo in mctx.predict(sctx.repos()):
                    target_name = model.config.predict.NAME
                    correct = Features_data[int(repo.key)]["Salary"]
                    prediction = repo.prediction(target_name).value
                    self.assertGreater(prediction, correct - (correct * 0.20))
                    self.assertLess(prediction, correct + (correct * 0.20))
