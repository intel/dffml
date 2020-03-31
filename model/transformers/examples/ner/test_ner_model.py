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
        if not list(filter(lambda line: line.startswith("Accuracy: "), lines)):
            raise AssertionError(f"Accuracy not found in: {lines}")
        # Check the predicted tag
        for line in lines:
            try:
                line = ast.literal_eval(line)
            except Exception:
                pass
            if type(line) == type({}):
                for d in line["Tag"][0]:
                    self.assertIn(
                        list(d.values())[0],
                        [
                            "O",
                            "B-MISC",
                            "I-MISC",
                            "B-PER",
                            "I-PER",
                            "B-ORG",
                            "I-ORG",
                            "B-LOC",
                            "I-LOC",
                        ],
                    )

    def test_python_filenames(self):
        with directory_with_csv_files() as tempdir:
            self.python_test("ner_model.py")

    def test_shell(self):
        with directory_with_csv_files() as tempdir:
            # Run training
            subprocess.check_output(["bash", sh_filepath("train.sh")])
            # Check the Accuracy
            stdout = subprocess.check_output(
                ["bash", sh_filepath("accuracy.sh")]
            )
            self.assertTrue(float(stdout.decode().strip()) >= 0.0)
            # Make the prediction
            stdout = subprocess.check_output(
                ["bash", sh_filepath("predict.sh")]
            )
            records = json.loads(stdout.decode())
            # Check the predicted ner tag
            for d in records[0]["prediction"]["Tag"]["value"][0]:
                self.assertIn(
                    list(d.values())[0],
                    [
                        "O",
                        "B-MISC",
                        "I-MISC",
                        "B-PER",
                        "I-PER",
                        "B-ORG",
                        "I-ORG",
                        "B-LOC",
                        "I-LOC",
                    ],
                )
