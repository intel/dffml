from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from dffml_feature_git.feature.operations import run_bandit
import os


class TestRunBanditOp(AsyncTestCase):
    async def test_run(self):
        async with run_bandit.imp(
            BaseConfig()
        ) as bandit_latest:
            async with bandit_latest(None, None) as ctx:
                results = await ctx.run({"repo": {
                    "URL": "dummy",
                    "directory": os.getcwd()
                    }
                })
                #print(results["score"])
                #self.assertGreaterEqual(float(results["score"]), 5.0)
