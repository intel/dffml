import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.model.model import ModelConfig
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, DefFeature, Features
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_scratch.model.misc import SLRContext


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
    [10.5, 124922.0]
]


class TestMisc(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = Misc(ModelConfig(directory=cls.model_dir.name, predict='Salary'))
        cls.feature = DefFeature('YearsExperience', float, 1)
        cls.features = Features(cls.feature)
        YearsExperience, Salary = list(zip(*FEATURE_DATA))
        cls.repos = [
            Repo(str(i),
                 data={'features': {
                     'YearsExperience': YearsExperience[i],
                     'Salary': Salary[i],
                     }}
                 )
            for i in range(0, len(Salary))
            ]
        cls.sources = \
            Sources(MemorySource(MemorySourceConfig(repos=cls.repos)))

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_context(self):
        async with self.sources as sources, self.features as features, \
                self.model as model:
            async with sources() as sctx, model() as mctx:
                # Test train
                await mctx.train(sctx, features)
                # Test accuracy
                res = await mctx.accuracy(sctx, features)
                self.assertGreater(res, 0.9)
                # Test predict
                res = [repo async for repo in mctx.predict(sctx.repos(),
                    features)]
                self.assertEqual(len(res), 1)
                self.assertEqual(res[0][0].src_url, a.src_url)
self.assertTrue(res[0][1])










'''
import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.model.model import ModelConfig
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, Feature, Features
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_scratch.model.misc import Misc

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
'''