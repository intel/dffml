import os
import random
import pathlib
import tempfile
from typing import Type

from dffml import train, predict, accuracy
from dffml.record import Record, RecordData
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Feature, Features
from dffml.util.cli.arg import parse_unknown
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_tensorflow.dnnc import (
    DNNClassifierModel,
    DNNClassifierModelConfig,
)


class TestDNN(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.feature = Feature("starts_with_a", int, 1)
        cls.features = Features(cls.feature)
        cls.records = [
            Record(
                "a" + str(random.random()),
                data={"features": {cls.feature.name: 1, "string": "a"}},
            )
            for _ in range(0, 1000)
        ]
        cls.records += [
            Record(
                "b" + str(random.random()),
                data={"features": {cls.feature.name: 0, "string": "not a"}},
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
                predict=Feature("string", str, 1),
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
            await parse_unknown(
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
                "-model-directory",
                self.model_dir.name,
            )
        )
        self.assertEqual(config.directory, pathlib.Path(self.model_dir.name))
        self.assertEqual(config.steps, 3000)
        self.assertEqual(config.epochs, 30)
        self.assertEqual(config.hidden, [12, 40, 15])
        self.assertEqual(config.predict.name, "feature_name")
        self.assertEqual(config.classifications, [0, 1, 2])
        self.assertEqual(config.clstype, int)

    async def test_model(self):
        for i in range(0, 7):
            await train(self.model, self.sources)
            res = await accuracy(self.model, self.sources)
            # Retry because of tensorflow intermitant low accuracy
            if res <= 0.9 and i < 5:
                print("Retry i:", i, "accuracy:", res)
                self.model_dir.cleanup()
                self.model_dir = tempfile.TemporaryDirectory()
                self.model.config = self.model.config._replace(
                    directory=self.model_dir.name
                )
                continue
            self.assertGreater(res, 0.9)
            a = Record("a", data={"features": {self.feature.name: 1}})
            target_name = self.model.config.predict.name
            res = [
                record
                async for record in predict(self.model, a, keep_record=True)
            ]
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].key, a.key)
            self.assertTrue(res[0].prediction(target_name).value)
