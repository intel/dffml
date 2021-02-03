import tempfile

from dffml import train, accuracy, predict, Feature, Features, AsyncTestCase

from REPLACE_IMPORT_PACKAGE_NAME.myslr import MySLRModel

TRAIN_DATA = [
    [12.4, 11.2],
    [14.3, 12.5],
    [14.5, 12.7],
    [14.9, 13.1],
    [16.1, 14.1],
    [16.9, 14.8],
    [16.5, 14.4],
    [15.4, 13.4],
    [17.0, 14.9],
    [17.9, 15.6],
    [18.8, 16.4],
    [20.3, 17.7],
    [22.4, 19.6],
    [19.4, 16.9],
    [15.5, 14.0],
    [16.7, 14.6],
]

TEST_DATA = [
    [17.3, 15.1],
    [18.4, 16.1],
    [19.2, 16.8],
    [17.4, 15.2],
    [19.5, 17.0],
    [19.7, 17.2],
    [21.2, 18.6],
]


class TestMySLRModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create an instance of the model
        cls.model = MySLRModel(
            features=Features(Feature("X", float, 1)),
            predict=Feature("Y", float, 1),
            directory=cls.model_dir.name,
        )

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory where the model was stored to cleanup
        cls.model_dir.cleanup()

    async def test_00_train(self):
        # Train the model on the training data
        await train(self.model, *[{"X": x, "Y": y} for x, y in TRAIN_DATA])

    async def test_01_accuracy(self):
        # Use the test data to assess the model's accuracy
        res = await accuracy(
            self.model, *[{"X": x, "Y": y} for x, y in TEST_DATA]
        )
        # Ensure the accuracy is above 80%
        self.assertTrue(0.8 <= res < 1.0)

    async def test_02_predict(self):
        # Get the prediction for each piece of test data
        async for i, features, prediction in predict(
            self.model, *[{"X": x, "Y": y} for x, y in TEST_DATA]
        ):
            # Grab the correct value
            correct = features["Y"]
            # Grab the predicted value
            prediction = prediction["Y"]["value"]
            # Check that the prediction is within 10% error of the actual value
            acceptable = 0.1
            self.assertLess(prediction, correct * (1.0 + acceptable))
            self.assertGreater(prediction, correct * (1.0 - acceptable))
