import pathlib
import unittest
import platform

from dffml import AsyncTestCase
from dffml.util.testing.consoletest.cli import main as consoletest


@unittest.skipIf(
    platform.system() in ["Windows", "Darwin"],
    f"Does not work on {platform.system()}",
)
class TestSWPortal(AsyncTestCase):
    async def test_readme(self):
        await consoletest(
            [
                str(
                    pathlib.Path(__file__).parents[2]
                    / "examples"
                    / "swportal"
                    / "README.rst"
                ),
                "--setup",
                str(
                    pathlib.Path(__file__).parent
                    / "swportal_consoletest_test_setup.py"
                ),
            ]
        )
