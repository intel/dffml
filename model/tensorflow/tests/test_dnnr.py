import os
import random
import pathlib
import tempfile
from typing import Type

import numpy as np

from dffml import train, accuracy, predict
from dffml.record import Record
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.util.cli.arg import parse_unknown
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature import Feature, Features

from dffml_model_tensorflow.dnnr import (
    DNNRegressionModel,
    DNNRegressionModelConfig,
)


class TestDNN(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.feature1 = Feature("feature_1", float, 1)
        cls.feature2 = Feature("feature_2", float, 1)
        cls.features = Features(cls.feature1, cls.feature2)
        cls.model = DNNRegressionModel(
            DNNRegressionModelConfig(
                directory=cls.model_dir.name,
                steps=1000,
                epochs=40,
                hidden=[50, 20, 10],
                predict=Feature("TARGET", float, 1),
                features=cls.features,
            )
        )
        # Generating data f(x1,x2) = 2*x1 + 3*x2
        _n_data = 2000
        _temp_data = np.random.rand(2, _n_data)
        cls.records = [
            Record(
                "x" + str(random.random()),
                data={
                    "features": {
                        cls.feature1.name: float(_temp_data[0][i]),
                        cls.feature2.name: float(_temp_data[1][i]),
                        "TARGET": 2 * _temp_data[0][i] + 3 * _temp_data[1][i],
                    }
                },
            )
            for i in range(0, _n_data)
        ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(records=cls.records))
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_config(self):
        # Setting up configuration for model
        config = self.model.__class__.config(
            await parse_unknown(
                "--model-predict",
                "TARGET:float:1",
                "--model-features",
                "feature_1:float:1",
                "--model-features",
                "feature_2:float:1",
                "-model-directory",
                self.model_dir.name,
            )
        )
        self.assertEqual(config.directory, pathlib.Path(self.model_dir.name))
        self.assertEqual(config.steps, 3000)
        self.assertEqual(config.epochs, 30)
        self.assertEqual(config.hidden, [12, 40, 15])
        self.assertEqual(config.predict.name, "TARGET")

    async def test_model(self):
        test_feature_val = [
            0,
            1.5,
            2,
        ]  # inserting zero so that its 1-indexable
        test_target = 2 * test_feature_val[1] + 3 * test_feature_val[2]
        # should be same function used in TestDNN.setupclass
        a = Record(
            "a",
            data={
                "features": {
                    self.feature1.name: test_feature_val[1],
                    self.feature2.name: test_feature_val[2],
                }
            },
        )
        target_name = self.model.config.predict.name
        for i in range(0, 7):
            await train(self.model, self.sources)
            res = await accuracy(self.model, self.sources)
            # Retry because of tensorflow intermitant low accuracy
            if res <= 0.8 and i < 5:
                print("Retry i:", i, "accuracy:", res)
                self.model_dir.cleanup()
                self.model_dir = tempfile.TemporaryDirectory()
                self.model.config = self.model.config._replace(
                    directory=self.model_dir.name
                )
                continue
            self.assertGreater(res, 0.8)
            res = [
                record
                async for record in predict(self.model, a, keep_record=True)
            ]
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].key, a.key)
            test_error_norm = abs(
                (test_target - res[0].prediction(target_name).value)
                / test_target
                + 1e-6
            )
            error_threshold = 0.3
            self.assertLess(test_error_norm, error_threshold)
