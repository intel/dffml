"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""

from dffml.cli.cli import CLI
from dffml.util.asynctestcase import AsyncTestCase


class TestCSV(AsyncTestCase):
    async def test_string_keys(self):
        # Test for issue #207
        self.required_plugins("dffml-model-scikit")
        # Create the training data
        train_filename = self.mktempfile(
            suffix=".csv",
            text="""
                Years,Expertise,Trust,Salary
                0,1,0.2,10
                1,3,0.4,20
                2,5,0.6,30
                3,7,0.8,40
                """,
        )
        # Create the test data
        test_filename = self.mktempfile(
            suffix=".csv",
            text="""
                Years,Expertise,Trust,Salary
                4,9,1.0,50
                5,11,1.2,60
                """,
        )
        # Create the prediction data
        predict_filename = self.mktempfile(
            suffix=".csv",
            text="""
                Years,Expertise,Trust
                6,13,1.4
                """,
        )
        # Features
        features = (
            "-model-features Years:int:1 Expertise:int:1 Trust:float:1".split()
        )
        model_dir = self.mktempdir()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "scikitlr",
            *features,
            "-model-predict",
            "Salary:float:1",
            "-model-location",
            model_dir,
            "-sources",
            "training_data=csv",
            "-source-filename",
            train_filename,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "scikitlr",
            *features,
            "-model-predict",
            "Salary:float:1",
            "-model-location",
            model_dir,
            "-sources",
            "test_data=csv",
            "-source-filename",
            test_filename,
            "-features",
            "Salary:float:1",
            "-scorer",
            "mse",
        )
        # Make prediction
        results = await CLI._main(
            "predict",
            "all",
            "-model",
            "scikitlr",
            *features,
            "-model-predict",
            "Salary:float:1",
            "-model-location",
            model_dir,
            "-sources",
            "predict_data=csv",
            "-source-filename",
            predict_filename,
        )
        self.assertTrue(isinstance(results, list))
        self.assertTrue(results)
        results = results[0].export()
        self.assertIn("key", results)
        self.assertEqual("0", results["key"])
        self.assertIn("prediction", results)
        self.assertIn("Salary", results["prediction"])
        results = results["prediction"]["Salary"]
        self.assertIn("value", results)
        self.assertEqual(70, round(results["value"]))
