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

from dffml_model_h2oautoml.h2oautoml import (
    H2oAutoMLModel,
    H2oAutoMLModelConfig,
)


class TestH2oAutoMLModel(IntegrationCLITestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create an instance of the model
        cls.model = H2oAutoMLModel(
            H2oAutoMLModelConfig(
                features=Features(
                    Feature("Feature1", float, 1), Feature("Feature2")
                ),
                predict=Feature("Target", float, 1),
                directory=cls.model_dir.name,
                max_models=5,
            )
        )

        # Generating data f(x1,x2) = 2*x1 + 3*x2
        _n_data = 200
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
            MemorySource(MemorySourceConfig(records=cls.records[:180]))
        )
        cls.testsource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[180:]))
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
        # Ensure the rmse is below 0.1
        self.assertTrue(0.1 > res)

    async def test_02_predict(self):
        # Sometimes causes an issue when only one data point anomalously has
        # high error. We count the number of errors and provide a threshold
        # over which the whole test errors
        unacceptable_error = 0
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
            if error > acceptable:
                unacceptable_error += 1

        # Test fails if more than N data points were out of acceptable error
        self.assertLess(unacceptable_error, 10)


class TestH2oAutoMLDocstring(IntegrationCLITestCase):
    async def test_docstring(self):
        # Console testing
        await run_consoletest(
            H2oAutoMLModel,
            docs_root_dir=pathlib.Path(__file__).parents[3] / "docs",
        )
