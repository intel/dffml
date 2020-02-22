import random
import tempfile
from typing import Type

from dffml.record import Record, RecordData
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
        return 1 if data.key.lower().startswith("a") else 0


class TestMisc(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.feature = StartsWithA()
        cls.features = Features(cls.feature)
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = MiscModel(
            MiscModelConfig(
                directory=cls.model_dir.name,
                classifications=["not a", "a"],
                features=cls.features,
            )
        )
        cls.records = [
            Record(
                "a" + str(random.random()),
                data={"features": {cls.feature.NAME: 1, "string": "a"}},
            )
            for _ in range(0, 1000)
        ]
        cls.records += [
            Record(
                "b" + str(random.random()),
                data={"features": {cls.feature.NAME: 0, "string": "not a"}},
            )
            for _ in range(0, 1000)
        ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(records=cls.records))
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                res = await mctx.accuracy(sctx)
                self.assertGreater(res, 0.9)

    async def test_02_predict(self):
        a = Record("a", data={"features": {self.feature.NAME: 1}})
        b = Record("not a", data={"features": {self.feature.NAME: 0}})
        async with Sources(
            MemorySource(MemorySourceConfig(records=[a, b]))
        ) as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                num = 0
                async for record, prediction, confidence in mctx.predict(
                    sctx.records()
                ):
                    with self.subTest(record=record):
                        self.assertEqual(prediction, record.key)
                    num += 1
                self.assertEqual(num, 2)
