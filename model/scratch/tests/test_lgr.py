import tempfile
import unittest

from dffml import train, accuracy, predict, Feature, Features, AsyncTestCase

from dffml_model_scratch.logisticregression import (
    LogisticRegressionConfig,
    LogisticRegression,
)

TRAIN_DATA = [
    [0.90, 0],
    [0.22, 0],
    [0.34, 0],
    [0.09, 0],
    [0.76, 0],
    [0.29, 0],
    [0.98, 0],
    [0.47, 0],
    [0.51, 1],
    [0.60, 1],
    [0.97, 1],
    [0.82, 1],
    [0.24, 1],
    [0.19, 1],
    [0.79, 1],
    [0.92, 1],
]

TEST_DATA = [
    [0.28, 1],
    [0.94, 0],
    [0.64, 1],
    [0.37, 1],
    [0.65, 0],
    [0.09, 1],
    [0.22, 0],
]


class TestLogisticRegression(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create the training data
        cls.train_data = []
        for x, y in TRAIN_DATA:
            cls.train_data.append({"X": x, "Y": y})
        # Create the test data
        cls.test_data = []
        for x, y in TEST_DATA:
            cls.test_data.append({"X": x, "Y": y})
        # Create an instance of the model
        cls.model = LogisticRegression(
            directory=cls.model_dir.name,
            predict=Feature("Y", float, 1),
            features=Features(Feature("X", float, 1)),
        )

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory where the trained model was stored
        cls.model_dir.cleanup()

    async def test_00_train(self):
        # Train the model on the training data
        await train(self.model, *self.train_data)

    async def test_01_accuracy(self):
        # Use the test data to assess the model's accuracy
        res = await accuracy(self.model, *self.test_data)
        # Ensure the accuracy is above 80%
        self.assertTrue(0.0 <= res <= 1.0)

    async def test_02_predict(self):
        # Get the prediction for each piece of test data
        async for i, features, prediction in predict(
            self.model, *self.test_data
        ):
            # Grab the correct value
            correct = self.test_data[i]["Y"]
            # Grab the predicted value
            prediction = prediction["Y"]["value"]
