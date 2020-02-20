import os

from shouldi.bandit import run_bandit

from dffml.util.asynctestcase import AsyncTestCase


class TestRunBanditOp(AsyncTestCase):
    async def test_run(self):
        results = await run_bandit(os.getcwd())
        self.assertEqual(
            type(results["report"]["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"]), int
        )
