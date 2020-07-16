import os
import ast
import sys
import json
import shutil
import pathlib
import tempfile
import contextlib
import subprocess
import unittest.mock
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
    async def test_shell(self):
        with directory_with_data_files() as tempdir:
            # Create the dataflow config files
            subprocess.check_output(
                ["bash", sh_filepath("create_dataflow.sh")]
            )
            # Run training
            subprocess.check_output(["bash", sh_filepath("train.sh")])
            # Check the Accuracy
            stdout = subprocess.check_output(
                ["bash", sh_filepath("accuracy.sh")]
            )
            self.assertRegex(stdout.decode().strip(), r"[-+]?\d*\.?\d+|\d+")

            # Make the prediction
            with open(sh_filepath("predict.sh"), "r") as cmd:
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
