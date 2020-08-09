import os
import ast
import sys
import json
import tempfile
import contextlib
import subprocess
import unittest.mock
import logging, sys

import numpy as np

from dffml.util.os import chdir


def sh_filepath(filename):
    return os.path.join(os.path.dirname(__file__), filename)


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(["bash", sh_filepath("train_data.sh")])
            subprocess.check_output(["bash", sh_filepath("test_data.sh")])
            yield tempdir


class TestExample(unittest.TestCase):
    def python_test(self, filename):
        # Path to target file
        filepath = os.path.join(os.path.dirname(__file__), filename)
        # Capture output
        stdout = subprocess.check_output([sys.executable, filepath])
        lines = stdout.decode().split("\n")
        # Check the Accuracy
        self.assertRegex(lines[0], r"Accuracy:  [-+]?\d*\.?\d+|\d+")
        # Check the ans
        self.assertIsInstance(ast.literal_eval(lines[1])["ans"], float)

    def test_python_filenames(self):
        with directory_with_csv_files() as tempdir:
            self.python_test("lr.py")

    def test_shell(self):
        with directory_with_csv_files() as tempdir:
            # Run training
            subprocess.check_output(["bash", sh_filepath("train.sh")])
            # Check the Accuracy
            stdout = subprocess.check_output(
                ["bash", sh_filepath("accuracy.sh")]
            )
            lines = stdout.decode().split("\n")
            self.assertRegex(lines[0], r"[-+]?\d*\.?\d+|\d+")
            # Make the prediction
            stdout = subprocess.check_output(
                ["bash", sh_filepath("predict.sh")]
            )
            records = json.loads(stdout.decode())
            # Check the ans
            self.assertIsInstance(
                records[0]["prediction"]["ans"]["value"], float
            )
