from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.safety import safety_check


class TestSafetyCheck(AsyncTestCase):
    async def test_run(self):
        async with safety_check.imp(BaseConfig()) as safety:
            async with safety(None, None) as ctx:
                results = await ctx.run(
                    {"package": "insecure-package", "version": "0.1.0"}
                )
                self.assertEqual(results["issues"], 1)
