import os
import sys
import random
import tempfile
import subprocess

import numpy as np
from sklearn.metrics import f1_score

from dffml.record import Record
from dffml.source.source import Sources
from dffml import train, score, predict, run_consoletest
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature.feature import Feature, Features
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.accuracy import ClassificationAccuracy

from dffml_model_xgboost.xgbclassifier import (
    XGBClassifierModel,
    XGBClassifierModelConfig,
)


class TestXGBClassifier(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create an instance of the model
        cls.model = XGBClassifierModel(
            XGBClassifierModelConfig(
                features=Features(
                    Feature("Feature1", float, 1), Feature("Feature2")
                ),
                predict=Feature("Target", float, 1),
                location=cls.model_dir.name,
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

        cls.trainingsource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[:1800]))
        )
        cls.testsource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[1800:]))
        )
        cls.scorer = ClassificationAccuracy()

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory where the model was stored to cleanup
        cls.model_dir.cleanup()

    async def test_00_train(self):
        # Train the model on the training data
        await train(self.model, self.trainingsource)

    async def test_01_accuracy(self):
        # Use the test data to assess the model's accuracy
        res = await score(
            self.model,
            self.scorer,
            Feature("Target", float, 1),
            self.testsource,
        )
        # Ensure the accuracy is above 80%
        self.assertTrue(0.8 <= res)

    async def test_02_predict(self):
        # reduce overfitting
        res_train = await score(
            self.model,
            self.scorer,
            Feature("Target", float, 1),
            self.trainingsource,
        )

        res_test = await score(
            self.model,
            self.scorer,
            Feature("Target", float, 1),
            self.testsource,
        )
        # Test fails if the difference between training and testing is more that 5%
        self.assertLess(res_train - res_test, 0.05)

    async def test_03_example(self):
        # Check for unstable data. you are using changes from giving you 0 to 1 binary information to –1 to 1,
        # then that could be detrimental to the output of the model.
        # unique values in target at training time
        unique_train = set()
        for c in self.records:
            unique_train.add(c.data.features["Target"])

        # unique values in target after prediction
        unique_predict = set()
        async for i, features, prediction in predict(
            self.model, self.testsource
        ):
            unique_predict.add(prediction["Target"]["value"])

        # values in both sets must be equal
        self.assertTrue(unique_predict == unique_train)

    async def test_04_example(self):
        # Check that model should also work better on imbalanced data
        # list of correct values of target
        correct = []
        # list of predicted values of target
        predictions = []
        async for i, features, prediction in predict(
            self.model, self.testsource
        ):
            correct.append(features["Target"])
            predictions.append(prediction["Target"]["value"])

        # calculate F1 score
        res = f1_score(correct, predictions, average="micro")

        # Ensure the F1 score is above 90%
        self.assertTrue(0.9 <= res)

    async def test_05_example(self):
        # Path to target file
        filepath = os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "iris_classification.py",
        )
        subprocess.check_call([sys.executable, filepath])


class TestXGBClassifierDocstring(AsyncTestCase):
    async def test_docstring(self):
        await run_consoletest(XGBClassifierModel)
