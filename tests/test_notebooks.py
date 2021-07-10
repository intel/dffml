import os
import pathlib
import unittest
import logging
import contextlib

from testbook import testbook

from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.os import chdir

TESTS_PATH = pathlib.Path(__file__).parent
NOTEBOOK_DATA_PATH = TESTS_PATH.joinpath("notebooks", "data")
NB_PATH = TESTS_PATH.parent / "examples" / "notebooks"


class TestNotebook(AsyncTestCase):
    """
    Class to test notebooks.
    Methods are generated in runtime to test notebooks present in `examples/notebooks`.
    """

    REQUIRED_PLUGINS = [
        "dffml-model-scikit",
        "dffml-model-xgboost",
    ]


def mk_notebook_test(path: pathlib.Path):
    def testcase(self):
        with chdir(NOTEBOOK_DATA_PATH):
            with testbook(path, execute=True) as tb:
                pass

    return testcase


method_base_name = "test_nb_"
# Make dir if it doesn't exist
NOTEBOOK_DATA_PATH.mkdir(parents=True, exist_ok=True)

for path in NB_PATH.glob("*.ipynb"):
    # Create the testcase
    test_case = mk_notebook_test(path)
    # Create the method name
    method_name = method_base_name + path.stem
    # Create the method
    setattr(TestNotebook, method_name, test_case)
