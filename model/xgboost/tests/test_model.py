import os
import sys
import random
import tempfile
import subprocess

import numpy as np

from dffml.record import Record
from dffml.base import config, field
from dffml.source.source import Sources
from dffml.model.accuracy import Accuracy
from dffml import train, accuracy, predict
from dffml.util.entrypoint import entrypoint
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature.feature import Feature, Features
from dffml.model.model import SimpleModel, ModelNotTrained
from dffml.source.memory import MemorySource, MemorySourceConfig


from dffml_model_xgboost.xgbregressor import (
    XGBRegressorModel,
    XGBRegressorModelConfig,
)


class TestXGBRegressor(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create an instance of the model
        cls.model = XGBRegressorModel(
            XGBRegressorModelConfig(
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
        # Use the test data to assess the model's accuracy
        res = await accuracy(self.model, self.testsource)
        # Ensure the accuracy is above 80%
        self.assertTrue(0.8 <= res)

    async def test_02_predict(self):
        # Get the prediction for each piece of test data
        async for i, features, prediction in predict(
            self.model, self.testsource
        ):
            # Grab the correct value
            correct = features["Target"]
            # Grab the predicted value
            prediction = prediction["Target"]["value"]
            # Check that the prediction is within 30% error of the actual value
            error = abs((prediction - correct) / correct)

            acceptable = 0.3
            # Sometimes causes an issue when only one data point anomalously has high error
            self.assertLess(error, acceptable)

    async def test_03_example(self):
        # Path to target file
        filepath = os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "diabetesregression.py",
        )
        subprocess.check_call([sys.executable, filepath])
