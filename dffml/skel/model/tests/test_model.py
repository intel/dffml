import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, Feature, Features
from dffml.util.asynctestcase import AsyncTestCase

from REPLACE_IMPORT_PACKAGE_NAME.misc import MiscModel, MiscModelConfig


class StartsWithA(Feature):

    NAME: str = "starts_with_a"

    def dtype(self) -> Type:
        return int

    def length(self) -> int:
        return 1

    async def calc(self, data: Data) -> int:
        return 1 if data.src_url.lower().startswith("a") else 0


class TestMisc(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = MiscModel(
            MiscModelConfig(
                directory=cls.model_dir.name, classifications=["not a", "a"]
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
        b = Repo("not a", data={"features": {self.feature.NAME: 0}})
        async with Sources(
            MemorySource(MemorySourceConfig(repos=[a, b]))
        ) as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                num = 0
                async for repo, prediction, confidence in mctx.predict(
                    sctx.repos()
                ):
                    with self.subTest(repo=repo):
                        self.assertEqual(prediction, repo.src_url)
                    num += 1
                self.assertEqual(num, 2)
