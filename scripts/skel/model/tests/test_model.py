import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.model.model import ModelConfig
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, Feature, Features
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_model_name.model.misc import Misc

class StartsWithA(Feature):

    NAME: str = 'starts_with_a'

    def dtype(self) -> Type:
        return int

    def length(self) -> int:
        return 1

    async def calc(self, data: Data) -> int:
        return 1 if data.src_url.lower().startswith('a') \
                else 0

class TestMisc(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = Misc(ModelConfig(directory=cls.model_dir.name))
        cls.feature = StartsWithA()
        cls.features = Features(cls.feature)
        cls.classifications = ['a', 'not a']
        cls.repos = [Repo('a' + str(random.random()),
            data={'features': {cls.feature.NAME: 1},
                'classification': 'a'}) for _ in range(0, 1000)]
        cls.repos += [Repo('b' + str(random.random()),
            data={'features': {cls.feature.NAME: 0},
                'classification': 'not a'}) for _ in range(0, 1000)]
        cls.sources = \
            Sources(MemorySource(MemorySourceConfig(repos=cls.repos)))

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        async with self.sources as sources, self.features as features, \
                self.model as model:
            async with sources() as sctx, model() as mctx:
                await mctx.train(sctx, features,
                        self.classifications)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.features as features, \
                self.model as model:
            async with sources() as sctx, model() as mctx:
                res = await mctx.accuracy(sctx, features,
                        self.classifications)
                self.assertGreater(res, 0.9)

    async def test_02_predict(self):
        a = Repo('a', data={'features': {self.feature.NAME: 1}})
        async with Sources(MemorySource(MemorySourceConfig(repos=[a]))) as sources, \
                self.features as features, \
                self.model as model:
            async with sources() as sctx, model() as mctx:
                res = [repo async for repo in mctx.predict(sctx.repos(),
                    features, self.classifications)]
                self.assertEqual(len(res), 1)
                self.assertEqual(res[0][0].src_url, a.src_url)
                self.assertTrue(res[0][1])
