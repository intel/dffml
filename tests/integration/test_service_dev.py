"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import io
import json
import inspect
import pathlib
import unittest.mock
from dffml.df.types import DataFlow
from dffml.cli.cli import CLI
from dffml.service.dev import Develop
from dffml.util.asynctestcase import IntegrationCLITestCase, relative_chdir


class TestDevelop(IntegrationCLITestCase):
    async def test_export(self):
        self.required_plugins("shouldi")
        stdout = io.StringIO()
        # Use shouldi's dataflow for tests
        with relative_chdir("..", "..", "examples", "shouldi"):
            with unittest.mock.patch("sys.stdout.buffer.write") as write:
                await Develop.cli("export", "shouldi.cli:DATAFLOW")
            DataFlow._fromdict(**json.loads(write.call_args[0][0]))

    async def test_run(self):
        self.required_plugins("dffml-model-scratch")
        # Create the training data
        filename = self.mktempfile() + ".csv"
        model_dir = self.mktempdir()
        pathlib.Path(filename).write_text(
            inspect.cleandoc(
                """
                Years,Salary
                1,40
                2,50
                3,60
                4,70
                5,80
                """
            )
            + "\n"
        )
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "slr",
            "-model-features",
            "Years:int:1",
            "-model-predict",
            "Salary:float:1",
            "-model-directory",
            model_dir,
            "-sources",
            "training_data=csv",
            "-source-filename",
            filename,
        )
        # Run the model_predict operation to use the trained model
        results = await Develop.cli(
            "run",
            "-log",
            "debug",
            "dffml.operation.model:model_predict",
            "-features",
            json.dumps({"Years": 6}),
            "-config-model",
            "slr",
            "-config-model-features",
            "Years:int:1",
            "-config-model-predict",
            "Salary:float:1",
            "-config-model-directory",
            model_dir,
        )
        self.assertIn("model_predictions", results)
        results = results["model_predictions"]
        self.assertIn("Salary", results)
        results = results["Salary"]
        self.assertIn("value", results)
        results = results["value"]
        self.assertEqual(results, 90.0)
