import os

from dffml.util.asynctestcase import AsyncTestCase

from shouldi.golangci_lint import run_golangci_lint


class TestRunGolangci_lintOp(AsyncTestCase):
    async def test_run(self):
        results = await run_golangci_lint(os.getcwd())
        self.assertEqual(type(results["issues"]), int)
