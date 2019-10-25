import os
import random
import tempfile
from typing import Type

import numpy as np
from dffml.repo import Repo, RepoData
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.feature import Data, Feature, Features
from dffml.util.cli.arg import parse_unknown
from dffml.util.asynctestcase import AsyncTestCase

from dffml_model_tensorflow.dnnr import (
    DNNRegressionModel,
    DNNRegressionModelConfig,
)

# Creating feature classes
class Feature_1(Feature):

    NAME: str = "feature_1"

    def dtype(self) -> Type:
        return float

    def length(self) -> int:
        return 1


class Feature_2(Feature):

    NAME: str = "feature_2"

    def dtype(self) -> Type:
        return float

    def length(self) -> int:
        return 1


class TestDNN(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = DNNRegressionModel(
            DNNRegressionModelConfig(
                directory=cls.model_dir.name,
                steps=1000,
                epochs=30,
                hidden=[10, 20, 10],
                predict="TARGET",
            )
        )
        cls.feature1 = Feature_1()
        cls.feature2 = Feature_2()
        cls.features = Features(cls.feature1, cls.feature2)
        # Generating data f(x1,x2) = 2*x1 + 3*x2
        _n_data = 1000
        _temp_data = np.random.rand(2, _n_data)
        cls.repos = [
            Repo(
                "x" + str(random.random()),
                data={
                    "features": {
                        cls.feature1.NAME: float(_temp_data[0][i]),
                        cls.feature2.NAME: float(_temp_data[1][i]),
                        "TARGET": 2 * _temp_data[0][i] + 3 * _temp_data[1][i],
                    }
                },
            )
            for i in range(0, _n_data)
        ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(repos=cls.repos))
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_config(self):
        # Setting up configuration for model
        config = self.model.__class__.config(
            parse_unknown("--model-predict", "TARGET")
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
        self.assertEqual(config.predict, "TARGET")

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

        test_feature_val = [
            0,
            1.5,
            2,
        ]  # inserting zero so that its 1-indexable
        test_target = 2 * test_feature_val[1] + 3 * test_feature_val[2]
        # should be same function used in TestDNN.setupclass
        a = Repo(
            "a",
            data={
                "features": {
                    self.feature1.NAME: test_feature_val[1],
                    self.feature2.NAME: test_feature_val[2],
                }
            },
        )
        async with Sources(
            MemorySource(MemorySourceConfig(repos=[a]))
        ) as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                res = [repo async for repo in mctx.predict(sctx.repos())]
                self.assertEqual(len(res), 1)
            self.assertEqual(res[0].src_url, a.src_url)
            test_error_norm = abs(
                (test_target - res[0].prediction().value) / test_target + 1e-6
            )
            error_threshold = 0.2
            self.assertLess(test_error_norm, error_threshold)
