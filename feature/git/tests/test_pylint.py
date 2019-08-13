from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from dffml_feature_git.feature.operations import get_pylint_score
import os


class TestRunPylintScore(AsyncTestCase):
    print(os.getcwd())
    async def test_run(self):
        async with get_pylint_score.imp(
            BaseConfig()
        ) as pylint_latest:
            async with pylint_latest(None, None) as ctx:
                results = await ctx.run({"repo": {
                    "URL": "dummy",
                    "directory": os.getcwd()
                    }
                })
                print(results["score"])
                self.assertGreaterEqual(float(results["score"]), 5.0)
