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

from dffml import chdir


def sh_filepath(filename):
    return os.path.join(os.path.dirname(__file__), filename)


@contextlib.contextmanager
def directory_with_data_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            # Replace Yann's website with GitHub mirror for stability
            image_data_sh_path = pathlib.Path(sh_filepath("image_data.sh"))
            image_data_sh_contents = image_data_sh_path.read_text().split("\n")
            # First line is the curl command
            curl = image_data_sh_contents[0].split()[:-1]
            # Make 4 curl commands and then append the sha validation
            image_data_sh_github_mirror_path = pathlib.Path(
                tempdir, "image_data.sh"
            )
            image_data_sh_github_mirror_path.write_text(
                "\n".join(
                    [
                        " ".join(curl + [url])
                        for url in [
                            "https://github.com/intel/dffml/files/4283897/train-labels-idx1-ubyte.gz",
                            "https://github.com/intel/dffml/files/4283898/train-images-idx3-ubyte.gz",
                            "https://github.com/intel/dffml/files/6138929/t10k-labels-idx1-ubyte.gz",
                            "https://github.com/intel/dffml/files/6138930/t10k-images-idx3-ubyte.gz",
                        ]
                    ]
                    + image_data_sh_contents[1:],
                )
            )
            subprocess.check_output(
                ["bash", str(image_data_sh_github_mirror_path)]
            )
            subprocess.check_output(["bash", sh_filepath("image_file.sh")])
            for image in pathlib.Path(__file__).parent.glob("*.png"):
                shutil.copy(str(image.absolute()), image.name)
            yield tempdir


class TestMNIST(unittest.TestCase):
    @unittest.skipIf(
        sys.version_info.major == 3 and sys.version_info.minor >= 8,
        "Tensorflow does not support Python 3.8",
    )
    def test_shell(self):
        with directory_with_data_files() as tempdir:
            # Create the dataflow config files
            subprocess.check_output(
                ["bash", sh_filepath("create_dataflow.sh")]
            )
            subprocess.check_output(
                ["bash", sh_filepath("create_dataflow_1.sh")]
            )
            # Run training
            subprocess.check_output(["bash", sh_filepath("train.sh")])
            # Check the Accuracy
            stdout = subprocess.check_output(
                ["bash", sh_filepath("accuracy.sh")]
            )
            self.assertRegex(stdout.decode().strip(), r"[-+]?\d*\.?\d+|\d+")
            # Make the prediction
            stdout = subprocess.check_output(
                ["bash", sh_filepath("predict.sh")]
            )
            records = json.loads(stdout.decode())
            # Check the label
            self.assertIsInstance(
                round(records[0]["predictions"]["label"]), int
            )
