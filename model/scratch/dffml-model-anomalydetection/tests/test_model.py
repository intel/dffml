import tempfile

from dffml import AsyncTestCase, Feature, Features, accuracy, predict, train
from dffml_model_anomalydetection.anomalydetection import AnomalyModel

class TestMySLRModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create an instance of the model
        cls.model = AnomalyModel(
            features=Features(Feature("A", int, 1), Feature("B", int, 2), Feature("C", int, 2), Feature("D", int, 2), Feature("E", int, 2), Feature("F", int, 2), Feature("G", int, 2), Feature("H", int, 2), Feature("I", int, 2), Feature("J", int, 2),Feature("K", int, 2),),
            predict=Feature("Y", int, 1),
            directory=cls.model_dir.name,
            k = 0.7
        )

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory where the model was stored to cleanup
        cls.model_dir.cleanup()

    async def test_00_train(self):
        # Train the model on the training data
        await train(self.model, "trainx1.csv")

    async def test_01_accuracy(self):
        # Use the test data to assess the model's accuracy
        res = await accuracy(self.model, "test1.csv")
        # Ensure the accuracy is above 80%
        self.assertTrue(0.8 <= res < 1.0)

    async def test_02_predict(self):
        right_prediction = 0
        wrong_prediction = 0
        # Get the prediction for each piece of test data
        async for i, features, prediction in predict(
            self.model, "test1.csv"
        ):
            # Grab the correct value
            correct = features["Y"]
            # Grab the predicted value
            prediction = prediction["Y"]["value"]
            if(prediction == correct):
                right_prediction += 1
            else :
                wrong_prediction += 1
        # Check that the prediction is within 5% error of the actual value
        acceptable = 0.95
        self.assertGreater(right_prediction, (right_prediction + wrong_prediction) * (acceptable))
