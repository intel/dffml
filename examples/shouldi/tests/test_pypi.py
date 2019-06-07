from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.pypi import pypi_latest_package_version


class TestPyPiLatestPackageVersion(AsyncTestCase):
    async def test_run(self):
        async with pypi_latest_package_version.imp(
            BaseConfig()
        ) as pypi_latest:
            async with pypi_latest(None, None) as ctx:
                results = await ctx.run({"package": "insecure-package"})
                self.assertEqual(results["version"], "0.1.0")
