import csv
import json
import pathlib
import contextlib

from dffml.cli.cli import CLI
from dffml.util.asynctestcase import IntegrationCLITestCase


class TestDAAL4PyLRModel(IntegrationCLITestCase):
    async def test_run(self):
        # Make a temporary directory to store the model
        directory = self.mktempdir()
        # Create the csv data
        d_temp = {True: 1, False: 0}
        data_filename = self.mktempfile() + ".csv"
        with open(pathlib.Path(data_filename), "w") as data_file:
            writer = csv.writer(data_file, delimiter=",")
            writer.writerow(["f1", "ans"])
            writer.writerows(
                [[i / 10, d_temp[i / 10 > 0.5]] for i in range(0, 10)]
            )
        # Arguments for the model
        model_args = [
            "-model",
            "daal4pylr",
            "-model-features",
            "f1:int:1",
            "-model-predict",
            "ans:int:1",
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
            self.assertEqual(len(results), 10)
            for i, result in enumerate(results):
                self.assertIn("prediction", result)
                result = result["prediction"]
                self.assertIn("ans", result)
                result = result["ans"]
                self.assertIn("value", result)
                result = result["value"]
