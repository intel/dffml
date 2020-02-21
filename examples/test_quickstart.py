import os
import ast
import sys
import json
import tempfile
import contextlib
import subprocess
import unittest.mock

from dffml.util.os import chdir


def sh_filepath(filename):
    return os.path.join(os.path.dirname(__file__), "quickstart", filename)


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(["sh", sh_filepath("train_data.sh")])
            subprocess.check_output(["sh", sh_filepath("test_data.sh")])
            subprocess.check_output(["sh", sh_filepath("predict_data.sh")])
            yield tempdir


class TestQuickstart(unittest.TestCase):
    def python_test(self, filename):
        # Path to target file
        filepath = os.path.join(os.path.dirname(__file__), filename)
        # Capture output
        stdout = subprocess.check_output([sys.executable, filepath])
        lines = stdout.decode().split("\n")
        # Check the Accuracy
        self.assertIn("Accuracy: 1.0", lines[0])
        # Check the salary
        self.assertEqual(ast.literal_eval(lines[1])["Salary"], 70)
        self.assertEqual(ast.literal_eval(lines[2])["Salary"], 80)

    def test_python(self):
        self.python_test("quickstart.py")

    def test_python_async(self):
        self.python_test("quickstart_async.py")

    def test_python_filenames(self):
        with directory_with_csv_files() as tempdir:
            self.python_test("quickstart_filenames.py")

    def test_shell(self):
        with directory_with_csv_files() as tempdir:
            # Run training
            subprocess.check_output(["sh", sh_filepath("train.sh")])
            # Check the Accuracy
            stdout = subprocess.check_output(
                ["sh", sh_filepath("accuracy.sh")]
            )
            self.assertEqual(stdout.decode().strip(), "1.0")
            # Make the prediction
            stdout = subprocess.check_output(["sh", sh_filepath("predict.sh")])
            repos = json.loads(stdout.decode())
            # Check the salary
            self.assertEqual(
                int(repos[0]["prediction"]["Salary"]["value"]), 70
            )
            self.assertEqual(
                int(repos[1]["prediction"]["Salary"]["value"]), 80
            )
