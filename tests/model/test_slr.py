import unittest

from dffml import SLRModel, run_consoletest, AsyncTestCase


class TestSLRModel(AsyncTestCase):
    async def test_docstring(self):
        await run_consoletest(SLRModel)
