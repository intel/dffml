import os
import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, Feature, Features
from dffml.util.cli.arg import parse_unknown
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_tensorflow.dnnc import (
    DNNClassifierModel,
    DNNClassifierModelConfig,
)


class StartsWithA(Feature):

    NAME: str = "starts_with_a"

    def dtype(self) -> Type:
        return int

    def length(self) -> int:
        return 1


class TestDNN(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = DNNClassifierModel(
            DNNClassifierModelConfig(
                directory=cls.model_dir.name,
                steps=1000,
                epochs=30,
                hidden=[10, 20, 10],
                classification="string",
                classifications=["a", "not a"],
                clstype=str,
            )
        )
        cls.feature = StartsWithA()
        cls.features = Features(cls.feature)
        cls.repos = [
            Repo(
                "a" + str(random.random()),
                data={"features": {cls.feature.NAME: 1, "string": "a"}},
            )
            for _ in range(0, 1000)
        ]
        cls.repos += [
            Repo(
                "b" + str(random.random()),
                data={"features": {cls.feature.NAME: 0, "string": "not a"}},
            )
            for _ in range(0, 1000)
        ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(repos=cls.repos))
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_config(self):
        config = self.model.__class__.config(
            parse_unknown(
                "--model-classification",
                "feature_name",
                "--model-classifications",
                "0",
                "1",
                "2",
                "--model-clstype",
                "int",
            )
        )
        self.assertEqual(
            config.directory,
            os.path.join(
                os.path.expanduser("~"), ".cache", "dffml", "tensorflow"
            ),
        )
        self.assertEqual(config.steps, 3000)
        self.assertEqual(config.epochs, 30)
        self.assertEqual(config.hidden, [12, 40, 15])
        self.assertEqual(config.classification, "feature_name")
        self.assertEqual(config.classifications, [0, 1, 2])
        self.assertEqual(config.clstype, int)

    async def test_00_train(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                res = await mctx.accuracy(sctx)
                self.assertGreater(res, 0.9)

    async def test_02_predict(self):
        a = Repo("a", data={"features": {self.feature.NAME: 1}})
        async with Sources(
            MemorySource(MemorySourceConfig(repos=[a]))
        ) as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                res = [repo async for repo in mctx.predict(sctx.repos())]
                self.assertEqual(len(res), 1)
            self.assertEqual(res[0].src_url, a.src_url)
            self.assertTrue(res[0].prediction().value)
