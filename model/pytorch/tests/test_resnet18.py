import os
import json
import shutil
import pathlib
import tempfile
import contextlib
import subprocess

from dffml.cli.cli import CLI
from dffml.util.os import chdir
from dffml.util.asynctestcase import IntegrationCLITestCase


def sh_filepath(sub_dir, filename):
    return os.path.join(
        os.path.dirname(__file__), "..", "examples", sub_dir, filename
    )


@contextlib.contextmanager
def directory_with_data_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(
                [
                    "curl",
                    "-LO",
                    "https://download.pytorch.org/tutorial/hymenoptera_data.zip",
                ]
            )
            subprocess.check_output(["unzip", "hymenoptera_data.zip"])
            subprocess.check_output(
                ["rm", "hymenoptera_data/train/ants/imageNotFound.gif"]
            )
            subprocess.check_output(
                ["bash", sh_filepath("resnet18", "unknown_data.sh")]
            )
            yield tempdir


class TestResNet18Model(IntegrationCLITestCase):
    async def test_shell(self):
        self.required_plugins("dffml-model-pytorch", "dffml-config-image")

        def clean_args(fd, directory):
            cmnd = " ".join(fd.readlines()).split("\\\n")
            cmnd = " ".join(cmnd).split()
            for idx, word in enumerate(cmnd):
                cmnd[idx] = word.strip()
            cmnd[cmnd.index("-model-directory") + 1] = directory
            return cmnd

        with directory_with_data_files() as tempdir:
            with open(sh_filepath("resnet18", "train.sh"), "r") as f:
                train_command = clean_args(f, tempdir)
            await CLI.cli(*train_command[1:])

            with open(sh_filepath("resnet18", "accuracy.sh"), "r") as f:
                accuracy_command = clean_args(f, tempdir)
            await CLI.cli(*accuracy_command[1:])

            with open(sh_filepath("resnet18", "predict.sh"), "r") as f:
                predict_command = clean_args(f, tempdir)

            with contextlib.redirect_stdout(self.stdout):
                await CLI._main(*predict_command[1:-1])
                results = json.loads(self.stdout.getvalue())
                self.assertTrue(isinstance(results, list))
                self.assertTrue(results)
                results = results[0]
                print(results)
                self.assertIn("prediction", results)
                results = results["prediction"]
                self.assertIn("label", results)
                results = results["label"]
                self.assertIn("value", results)
                self.assertIn("confidence", results)
                self.assertIn(isinstance(results["value"], str), [True])
                self.assertTrue(results["confidence"])
