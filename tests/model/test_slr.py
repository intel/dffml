import pathlib
import unittest

from dffml import SLRModel, run_consoletest, AsyncTestCase


class TestSLRModel(AsyncTestCase):
    async def test_docstring(self):
        await run_consoletest(
            SLRModel, docs_root_dir=pathlib.Path(__file__).parents[2] / "docs",
        )
