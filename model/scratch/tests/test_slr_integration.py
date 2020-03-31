import csv
import json
import pathlib
import contextlib

from dffml.cli.cli import CLI
from dffml.util.asynctestcase import IntegrationCLITestCase


class TestSLR(IntegrationCLITestCase):
    async def test_run(self):
        # Make a temporary directory to store the model
        directory = self.mktempdir()
        # Create the csv data
        data_filename = self.mktempfile() + ".csv"
        with open(pathlib.Path(data_filename), "w") as data_file:
            writer = csv.writer(data_file, delimiter=",")
            writer.writerow(["Years", "Salary"])
            writer.writerows([[i, i * 10 + 30] for i in range(0, 6)])
        # Arguments for the model
        model_args = [
            "-model",
            "slr",
            "-model-features",
            "Years:int:1",
            "-model-predict",
            "Salary:int:1",
            "-model-directory",
            directory,
        ]
        # Train the model
        await CLI.cli(
            "train",
            *model_args,
            "-sources",
            "training_data=csv",
            "-source-filename",
            data_filename,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            *model_args,
            "-sources",
            "test_data=csv",
            "-source-filename",
            data_filename,
        )
        with contextlib.redirect_stdout(self.stdout):
            # Make prediction
            await CLI._main(
                "predict",
                "all",
                *model_args,
                "-sources",
                "predict_data=csv",
                "-source-filename",
                data_filename,
            )
            results = json.loads(self.stdout.getvalue())
            self.assertTrue(isinstance(results, list))
            self.assertEqual(len(results), 6)
            for i, result in enumerate(results):
                self.assertIn("prediction", result)
                result = result["prediction"]
                self.assertIn("Salary", result)
                result = result["Salary"]
                self.assertIn("value", result)
                result = result["value"]
                self.assertEqual(round(result), i * 10 + 30)
