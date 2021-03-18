import os

from dffml import AsyncTestCase

from shouldi.python.bandit import run_bandit


class TestRunBanditOp(AsyncTestCase):
    async def test_run(self):
        results = await run_bandit.test(pkg=os.getcwd())
        self.assertEqual(
            type(results["result"]["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"]), int
        )
