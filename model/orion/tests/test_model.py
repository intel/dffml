import tempfile

from dffml import train, accuracy, predict, Feature, Features, AsyncTestCase

from dffml_model_orion.orion_model import OrionModel


class TestOrionModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory(
            dir="dffml_model_orion/model"
        )
        # Create an instance of the model
        cls.model = OrionModel(
            data="./tests/train.csv",
            predict="./tests/predict.csv",
            accuracy="./tests/test.csv",
        )

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory where the model was stored to cleanup
        cls.model_dir.cleanup()

    async def test_00_train(self):
        # Train the model on the training data
        await train(self.model)

    async def test_01_accuracy(self):
        # Use the test data to assess the model's accuracy
        res = await accuracy(self.model)
        # Ensure the accuracy is above 80%
        self.assertTrue(0.8 <= res < 1.0)

    async def test_02_predict(self):
        # Get the prediction for each piece of test data
        async for i, features, prediction in predict(self.model):
            print(features["predict"])
