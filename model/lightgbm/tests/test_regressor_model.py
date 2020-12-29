import os
import pathlib
import random
import subprocess
import sys
import tempfile

import numpy as np
from dffml import accuracy, predict, run_consoletest, train
from dffml.base import config, field
from dffml.feature.feature import Feature, Features
from dffml.model.accuracy import Accuracy
from dffml.model.model import ModelNotTrained, SimpleModel
from dffml.record import Record
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.source.source import Sources
from dffml.util.asynctestcase import IntegrationCLITestCase
from dffml.util.entrypoint import entrypoint
from sklearn.metrics import mean_squared_error

from dffml_model_lightgbm.lgbmregressor import (
    LGBMRegressorModel,
    LGBMRegressorModelConfig,
)


class TestLGBMRegressor(IntegrationCLITestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create an instance of the model
        cls.model = LGBMRegressorModel(
            LGBMRegressorModelConfig(
                features=Features(
                    Feature("Feature1", float, 1), Feature("Feature2")
                ),
                predict=Feature("Target", float, 1),
                directory=cls.model_dir.name,
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
                        "Feature1": float(_temp_data[0][i]),
                        "Feature2": float(_temp_data[1][i]),
                        "Target": 2 * _temp_data[0][i] + 3 * _temp_data[1][i],
                    }
                },
            )
            for i in range(0, _n_data)
        ]

        # Splitting the training and test data set
        cls.trainingsource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[:1800]))
        )
        cls.testsource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[1800:]))
        )

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory where the model was stored to cleanup
        cls.model_dir.cleanup()

    async def test_00_train(self):
        # Train the model on the training data
        await train(self.model, self.trainingsource)

    async def test_01_accuracy(self):
        # Use the test data to assess the model's accuracy (mean squared error)

        ytrue = []
        ypred = []

        async for i, features, prediction in predict(
            self.model, self.testsource
        ):
            # Grab the correct value
            ytrue.append(features["Target"])
            # Grab the predicted value
            ypred.append(prediction["Target"]["value"])

        res = mean_squared_error(ytrue, ypred)

        # Ensure that the mean squared error should be less than
        self.assertTrue(1 >= res)

    async def test_02_accuracy(self):
        # Reduce overfitting

        # ----------- Find testing mse---------------
        testtrue = []
        testpred = []

        async for i, features, prediction in predict(
            self.model, self.testsource
        ):
            # Grab the correct value
            testtrue.append(features["Target"])
            # Grab the predicted value
            testpred.append(prediction["Target"]["value"])

        testRes = mean_squared_error(testtrue, testpred)

        # ---------- Find training mse---------------
        traintrue = []
        trainpred = []

        async for i, features, prediction in predict(
            self.model, self.trainingsource
        ):
            # Grab the correct value
            traintrue.append(features["Target"])
            # Grab the predicted value
            trainpred.append(prediction["Target"]["value"])

        trainRes = mean_squared_error(traintrue, trainpred)

        # Test fails if the difference between training and testing is more that 5%
        self.assertLess(testRes - trainRes, 0.05)

    async def test_docstring(self):
        await run_consoletest(
            LGBMRegressorModel,
            docs_root_dir=pathlib.Path(__file__).parents[3] / "docs",
        )
