import tempfile

from dffml import train, accuracy, predict, Feature, Features, AsyncTestCase

from dffml_model_daal4py.daal4pylr import DAAL4PyLRModel

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
    [17.9, 15.6],
    [18.8, 16.4],
    [20.3, 17.7],
    [22.4, 19.6],
    [19.4, 16.9],
    [15.5, 14.0],
    [16.7, 14.6],
]


class TestDAAL4PyLRModel(AsyncTestCase):
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
        cls.model = DAAL4PyLRModel(
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
        self.assertGreater(res, 0)

    async def test_02_predict(self):
        # Get the prediction for each piece of test data
        async for i, features, prediction in predict(
            self.model, *self.test_data
        ):
            # Grab the correct value
            correct = self.test_data[i]["Y"]
            # Grab the predicted value
            prediction = prediction["Y"]["value"]
            # Check that the percent error is less than 10%
            self.assertLess(prediction, correct * 1.1)
            self.assertGreater(prediction, correct * (1.0 - 0.1))
