import os
import csv
import json
import random
import string
import pathlib
import tempfile
import contextlib
import subprocess

from dffml.cli.cli import CLI
from dffml.util.os import chdir
from dffml.service.dev import Develop
from dffml.util.asynctestcase import IntegrationCLITestCase


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(
                [
                    "bash",
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        "examples",
                        "autoclassifier",
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
                        "autoclassifier",
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
                        "autoclassifier",
                        "predict_data.sh",
                    ),
                ]
            )
            yield tempdir


class TestAutoClassifierModel(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-autosklearn")

        def clean_args(fd, directory):
            cmnd = " ".join(fd.readlines()).split("\\\n")
            cmnd = " ".join(cmnd).split()
            for idx, word in enumerate(cmnd):
                cmnd[idx] = word.strip()
            cmnd[cmnd.index("-model-directory") + 1] = directory
            return cmnd

        with directory_with_csv_files() as tempdir:
            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "examples",
                    "autoclassifier",
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
                    "autoclassifier",
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
                    "autoclassifier",
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
                self.assertIn("classification", results)
                results = results["classification"]
                self.assertIn("value", results)
                self.assertIn("confidence", results)
                self.assertEqual(results["value"], 1)
                self.assertGreaterEqual(results["confidence"], 0.3)
