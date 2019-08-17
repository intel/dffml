from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.bandit import run_bandit
import os


class TestRunBanditOp(AsyncTestCase):
    async def test_run(self):
        async with run_bandit.imp(BaseConfig()) as bandit_latest:
            async with bandit_latest(None, None) as ctx:
                results = await ctx.run({"repo": {
                    "URL": "dummy",
                    "directory": os.getcwd()
                    }
                })
                self.assertLessEqual(int(results['report']
                            ["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"]), 5.0)
