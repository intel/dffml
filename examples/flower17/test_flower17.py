import os
import shutil
import pathlib
import tempfile
import contextlib
import subprocess
import shlex

from dffml.util.os import chdir
from dffml.cli.cli import CLI
from dffml.util.asynctestcase import IntegrationCLITestCase


def sh_filepath(filename):
    return os.path.join(os.path.dirname(__file__), filename)


@contextlib.contextmanager
def directory_with_data_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(["bash", sh_filepath("dataset.sh")])
            subprocess.check_output(["tar", "-xzf", "17flowers.tgz"])
            subprocess.check_output(["python3", sh_filepath("split.py")])
            subprocess.check_output(["bash", sh_filepath("unknown_data.sh")])
            for image in pathlib.Path(__file__).parent.glob("*.jpg"):
                shutil.copy(str(image.absolute()), image.name)
            yield tempdir


class TestFLOWER17(IntegrationCLITestCase):
    async def test_shell_sklearn(self):
        with directory_with_data_files() as tempdir:
            # Create the dataflow config files
            subprocess.check_output(
                ["bash", sh_filepath("sklearn-opencv/create_dataflow.sh")]
            )
            # Run training
            subprocess.check_output(
                ["bash", sh_filepath("sklearn-opencv/train.sh")]
            )
            # Check the Accuracy
            stdout = subprocess.check_output(
                ["bash", sh_filepath("sklearn-opencv/accuracy.sh")]
            )
            self.assertRegex(stdout.decode().strip(), r"[-+]?\d*\.?\d+|\d+")

            # Make the prediction
            with open(sh_filepath("sklearn-opencv/predict.sh"), "r") as cmd:
                cmd = cmd.read()
                cmd = cmd.replace("\n", "")
                cmd = cmd.replace("\\", "")
                cmd = shlex.split(cmd)
                # When passing to CLI, remove first argument(dffml) and -pretty at the end
                cmd = cmd[1:-1]
                records = await CLI.cli(*cmd)

                # Check the label for 1 record
                self.assertIsInstance(
                    records[0].prediction("label")["value"], str
                )

    async def test_shell_pytorch(self):
        with directory_with_data_files() as tempdir:
            # Run training
            subprocess.check_output(
                ["bash", sh_filepath("pytorch-alexnet/train.sh")]
            )
            # Check the Accuracy
            stdout = subprocess.check_output(
                ["bash", sh_filepath("pytorch-alexnet/accuracy.sh")]
            )
            self.assertRegex(stdout.decode().strip(), r"[-+]?\d*\.?\d+|\d+")

            # Make the prediction
            with open(sh_filepath("pytorch-alexnet/predict.sh"), "r") as cmd:
                cmd = cmd.read()
                cmd = cmd.replace("\n", "")
                cmd = cmd.replace("\\", "")
                cmd = shlex.split(cmd)
                # When passing to CLI, remove first argument(dffml) and -pretty at the end
                cmd = cmd[1:-1]
                records = await CLI.cli(*cmd)

                # Check the label for 1 record
                self.assertIsInstance(
                    records[0].prediction("label")["value"], str
                )
                self.assertTrue(
                    records[0].prediction("label")["confidence"] >= 0.99
                )
