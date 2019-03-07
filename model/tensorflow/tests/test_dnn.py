import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.source import Sources, RepoSource
from dffml.feature import Data, Feature, Features
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_tensorflow.model.dnn import DNN

class StartsWithA(Feature):

    NAME: str = 'starts_with_a'

    def dtype(self) -> Type:
        return int

    def length(self) -> int:
        return 1

    async def calc(self, data: Data) -> int:
        return 1 if data.src_url.lower().startswith('a') \
                else 0

class TestDNN(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = DNN()
        cls.model.model_dir = cls.model_dir.name
        cls.feature = StartsWithA()
        cls.features = Features(cls.feature)
        cls.classifications = ['a', 'not a']
        cls.repos = [Repo('a' + str(random.random()),
            data={'features': {cls.feature.NAME: 1},
                'classification': 'a'}) for _ in range(0, 1000)]
        cls.repos += [Repo('b' + str(random.random()),
            data={'features': {cls.feature.NAME: 0},
                'classification': 'not a'}) for _ in range(0, 1000)]
        cls.sources = Sources(RepoSource(*cls.repos))

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        async with self.sources as sources, self.features as features:
            await self.model.train(sources, features,
                    self.classifications, steps=1000,
                    num_epochs=30)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.features as features:
            res = await self.model.accuracy(sources, features,
                    self.classifications)
            self.assertGreater(res, 0.9)

    async def test_02_predict(self):
        a = Repo('a', data={'features': {self.feature.NAME: 1}})
        sources = Sources(RepoSource(a))
        async with sources as sources, self.features as features:
            res = [repo async for repo in self.model.predict(sources.repos(),
                features, self.classifications)]
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0][0].src_url, a.src_url)
            self.assertTrue(res[0][1])
