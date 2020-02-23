import os
import random
import tempfile
from typing import Type

from dffml.record import Record, RecordData
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, Feature, Features, DefFeature
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
        cls.feature = StartsWithA()
        cls.features = Features(cls.feature)
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
        cls.model = DNNClassifierModel(
            DNNClassifierModelConfig(
                directory=cls.model_dir.name,
                steps=1000,
                epochs=40,
                hidden=[50, 20, 10],
                predict=DefFeature("string", str, 1),
                classifications=["a", "not a"],
                clstype=str,
                features=cls.features,
            )
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_config(self):
        config = self.model.__class__.config(
            parse_unknown(
                "--model-predict",
                "feature_name:int:1",
                "--model-classifications",
                "0",
                "1",
                "2",
                "--model-clstype",
                "int",
                "--model-features",
                "starts_with_a:int:1",
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
        self.assertEqual(config.predict.NAME, "feature_name")
        self.assertEqual(config.classifications, [0, 1, 2])
        self.assertEqual(config.clstype, int)

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
        async with Sources(
            MemorySource(MemorySourceConfig(records=[a]))
        ) as sources, self.model as model:
            target_name = model.config.predict.NAME
            async with sources() as sctx, model() as mctx:
                res = [record async for record in mctx.predict(sctx.records())]
                self.assertEqual(len(res), 1)
            self.assertEqual(res[0].key, a.key)
            self.assertTrue(res[0].prediction(target_name).value)
