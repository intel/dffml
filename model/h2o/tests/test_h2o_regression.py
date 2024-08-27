import os
import tempfile
import contextlib
import subprocess

from dffml.cli.cli import CLI
from dffml.util.os import chdir
from dffml.util.asynctestcase import AsyncTestCase


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            p = subprocess.check_output(
                [
                    "bash",
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        "examples",
                        "regression",
                        "train_data.sh",
                    ),
                ]
            )
   
            subprocess.check_output(
                [
                    "bash",
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        "examples",
                        "regression",
                        "test_data.sh",
                    ),
                ]
            )
      
            subprocess.check_output(
                [
                    "bash",
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        "examples",
                        "regression",
                        "predict_data.sh",
                    ),
                ]
            )

            yield tempdir


class TestH2ORegressionModel(AsyncTestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-autoh2o")
 
        def clean_args(fd, directory):
            cmnd = " ".join(fd.readlines()).split("\\\n")
            cmnd = " ".join(cmnd).split()
            for idx, word in enumerate(cmnd):
                cmnd[idx] = word.strip()
            cmnd[cmnd.index("-model-location") + 1] = directory
            return cmnd

        with directory_with_csv_files() as tempdir:
            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "examples",
                    "regression",
                    "train.sh",
                ),
                "r",
            ) as f:
                train_cmnd = clean_args(f, tempdir)
            await CLI.cli(*train_cmnd[1:])

            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "examples",
                    "regression",
                    "accuracy.sh",
                ),
                "r",
            ) as f:
                accuracy_cmnd = clean_args(f, tempdir)
            await CLI.cli(*accuracy_cmnd[1:])

            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "examples",
                    "regression",
                    "predict.sh",
                ),
                "r",
            ) as f:
                predict_cmnd = clean_args(f, tempdir)
                results = await CLI._main(*predict_cmnd[1:])
                self.assertTrue(isinstance(results, list))
                self.assertTrue(results)
                results = results[0].export()
                self.assertIn("prediction", results)
                results = results["prediction"]
                self.assertIn("TARGET", results)
                results = results["TARGET"]
                self.assertIn("value", results)
                self.assertAlmostEqual(results["value"], 3.639936099771113, 2)
      
