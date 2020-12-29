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
from sklearn.metrics import f1_score

from dffml_model_lightgbm.lgbmclassifier import (
    LGBMClassifierModel,
    LGBMClassifierModelConfig,
)


class TestLGBMClassifier(IntegrationCLITestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()

        # Create an instance of the model
        cls.model = LGBMClassifierModel(
            LGBMClassifierModelConfig(
                features=Features(
                    Feature("Feature1", float, 1), Feature("Feature2")
                ),
                predict=Feature("Target", float, 1),
                directory=cls.model_dir.name,
            )
        )

        # Generating data f(x1,x2) = (2*x1 + 3*x2)//2
        _n_data = 2000
        _temp_data = np.random.rand(2, _n_data)
        cls.records = [
            Record(
                "x" + str(random.random()),
                data={
                    "features": {
                        "Feature1": float(_temp_data[0][i]),
                        "Feature2": float(_temp_data[1][i]),
                        "Target": (2 * _temp_data[0][i] + 3 * _temp_data[1][i])
                        // 2,
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
        # Use the test data to assess the model's accuracy
        res = await accuracy(self.model, self.testsource)
        # Ensure the accuracy is above 80%
        self.assertTrue(0.8 <= res)

    async def test_02_predict(self):
        # Reduce overfitting

        # Grab the accuracy on train and test set respectively.
        res_train = await accuracy(self.model, self.trainingsource)

        res_test = await accuracy(self.model, self.testsource)

        # Test fails if the difference between training and testing is more that 5%
        self.assertLess(res_train - res_test, 0.05)

    async def test_03_example(self):
        # Check for unstable data. you are using changes from giving you 0 to 1 binary information to –1 to 1,then that could be detrimental to the output of the model.
        # Unique values in target at training time
        unique_train = set()
        for c in self.records:
            unique_train.add(c.data.features["Target"])

        # Unique values in target after prediction
        unique_predict = set()
        async for i, features, prediction in predict(
            self.model, self.testsource
        ):
            unique_predict.add(prediction["Target"]["value"])

        # Values in both sets must be equal
        self.assertTrue(unique_predict == unique_train)

    async def test_04_example(self):
        # Check that model should also work better on imbalanced data
        # List of correct values of target
        correct = []
        # List of predicted values of target
        predictions = []
        async for i, features, prediction in predict(
            self.model, self.testsource
        ):
            correct.append(features["Target"])
            predictions.append(prediction["Target"]["value"])

        # Calculate F1 score
        res = f1_score(correct, predictions, average="micro")

        # Ensure the F1 score is above 90%
        self.assertTrue(0.9 <= res)

    async def test_docstring(self):
        await run_consoletest(
            LGBMClassifierModel,
            docs_root_dir=pathlib.Path(__file__).parents[3] / "docs",
        )
