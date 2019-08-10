from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from dffml_feature_git.feature.operations import get_pylint_score
import os


class TestRunPylintScore(AsyncTestCase):
    async def test_run(self):
        async with get_pylint_score.imp(
            BaseConfig()
        ) as pylint_latest:
            async with pylint_latest(None, None) as ctx:
                results = await ctx.run({"repo": {"directory": os.getcwd()}})
                print(results)
                self.assertEqual(results["score"], "test")
