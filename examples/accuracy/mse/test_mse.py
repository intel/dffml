import os
import ast
import sys
import json
import tempfile
import contextlib
import subprocess
import unittest.mock

from dffml import chdir


def sh_filepath(filename):
    return os.path.join(os.path.dirname(__file__), filename)


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(["bash", sh_filepath("dataset.sh")])
            yield tempdir


class TestExample(unittest.TestCase):
    def python_test(self, filename):
        # Path to target file
        filepath = os.path.join(os.path.dirname(__file__), filename)
        # Capture output
        stdout = subprocess.check_output([sys.executable, filepath])
        lines = stdout.decode().split("\n")
        # Check the Accuracy
        self.assertEqual(lines[0].split()[0], "Accuracy:")
        self.assertEqual(round(float(lines[0].split()[1])), 1)

    def test_python_filenames(self):
        with directory_with_csv_files() as tempdir:
            self.python_test("mse.py")
