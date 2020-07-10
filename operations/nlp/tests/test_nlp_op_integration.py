import os
import json
import random
import tempfile
import contextlib
import subprocess

from dffml.cli.cli import CLI
from dffml.util.os import chdir
from dffml.util.asynctestcase import IntegrationCLITestCase


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(
                [
                    "bash",
                    os.path.join(
                        os.path.expanduser("~"),
                        "dffml",
                        "examples",
                        "nlp",
                        "train_data.sh",
                    ),
                ]
            )
            subprocess.check_output(
                [
                    "bash",
                    os.path.join(
                        os.path.expanduser("~"),
                        "dffml",
                        "examples",
                        "nlp",
                        "test_data.sh",
                    ),
                ]
            )
            yield tempdir


class TestNLPOps(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-operations-nlp")

        # Test .sh files
        def clean_args(fd, directory):
            cmnd = " ".join(fd.readlines()).split("\\\n")
            cmnd = " ".join(cmnd).split()
            for idx, word in enumerate(cmnd):
                cmnd[idx] = word.strip()
            cmnd[cmnd.index("-model-directory") + 1] = directory
            cmnd[cmnd.index("-source-text-dataflow") + 1] = os.path.join(
                os.path.expanduser("~"),
                "dffml",
                "examples",
                "nlp",
                "nlp_ops_dataflow.yaml",
            )
            return cmnd

        with directory_with_csv_files() as tempdir:
            with open(
                os.path.join(
                    os.path.expanduser("~"),
                    "dffml",
                    "examples",
                    "nlp",
                    "train.sh",
                ),
                "r",
            ) as f:
                train_cmnd = clean_args(f, tempdir)
            await CLI.cli(*train_cmnd[1:])

            with open(
                os.path.join(
                    os.path.expanduser("~"),
                    "dffml",
                    "examples",
                    "nlp",
                    "accuracy.sh",
                ),
                "r",
            ) as f:
                accuracy_cmnd = clean_args(f, tempdir)
            await CLI.cli(*accuracy_cmnd[1:])

            with open(
                os.path.join(
                    os.path.expanduser("~"),
                    "dffml",
                    "examples",
                    "nlp",
                    "predict.sh",
                ),
                "r",
            ) as f:
                predict_cmnd = clean_args(f, tempdir)
            with contextlib.redirect_stdout(self.stdout):
                await CLI._main(*predict_cmnd[1:])
                results = json.loads(self.stdout.getvalue())
                self.assertTrue(isinstance(results, list))
                self.assertTrue(results)
                results = results[0]
                self.assertIn("prediction", results)
                results = results["prediction"]
                self.assertIn("sentiment", results)
                results = results["sentiment"]
                self.assertIn("value", results)
                results = results["value"]
                self.assertTrue(results in [0, 1])
