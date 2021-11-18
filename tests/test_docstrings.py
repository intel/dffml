import sys
import pathlib

from dffml.util.testing.docstrings import make_docstring_tests


REPO_ROOT = pathlib.Path(__file__).parents[1]

for TestCase in make_docstring_tests(REPO_ROOT):
    setattr(sys.modules[__name__], TestCase.__qaulname__, TestCase)
