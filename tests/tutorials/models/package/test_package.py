import os
import ast
import sys
import json
import venv
import shlex
import asyncio
import pathlib
import tempfile
import unittest
import contextlib
import subprocess

from dffml import chdir, mkvenv


def filepath(filename):
    return os.path.join(os.path.dirname(__file__), filename)


class TestPackage(unittest.TestCase):
    def test_package(self):
        with mkvenv() as tempdir:
            with chdir(tempdir):
                subprocess.check_call(["sh", filepath("create.sh")])
                subprocess.check_call(["sh", filepath("cd.sh")])
                cd_path = pathlib.Path(filepath("cd.sh"))
                pkg = cd_path.read_text().strip().split()[-1]
                with chdir(pkg):
                    # Check that the imports header is correct
                    check_imports_path = pathlib.Path(
                        filepath("test_model_imports.txt")
                    )
                    check_imports = check_imports_path.read_text().strip()
                    real_imports_path = pathlib.Path("tests", "test_model.py")
                    real_imports = real_imports_path.read_text().strip()
                    self.assertTrue(real_imports.startswith(check_imports))
                    # Run the pip install
                    subprocess.check_call(["sh", filepath("pip_install.sh")])
                    # Run the tests
                    subprocess.check_call(["sh", filepath("unittest.sh")])
                    subprocess.check_call(
                        ["sh", filepath("unittest_logging.sh")]
                    )
                    # Try training
                    subprocess.check_call(
                        [
                            "sh",
                            str(
                                pathlib.Path(__file__).parent.parent
                                / "slr"
                                / "train_data.sh"
                            ),
                        ]
                    )
                    subprocess.check_call(["sh", filepath("train.sh")])
