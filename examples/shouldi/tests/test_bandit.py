import os

from dffml.util.asynctestcase import AsyncTestCase

from shouldi.bandit import run_bandit


class TestRunBanditOp(AsyncTestCase):
    async def test_run(self):
        results = await run_bandit(os.getcwd())
        self.assertLessEqual(
            int(results["report"]["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"]), 5.0
        )
