import json
from pathlib import Path

from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.pypi import pypi_package_json
from shouldi.pypi import pypi_latest_package_version
from shouldi.pypi import pypi_package_url


class TestPyPiOperations(AsyncTestCase):
    PACKAGE = "insecure-package"
    INT_RESULT_JSON = {}

    async def test_000_package_json(self):
        async with pypi_package_json.imp(BaseConfig()) as pypi_package:
            async with pypi_package(None, None) as ctx:
                results = await ctx.run({"package": self.PACKAGE})
                self.assertIs(type(results["response_json"]), dict)
                self.INT_RESULT_JSON.update(results["response_json"])

    async def test_001_package_version(self):
        async with pypi_latest_package_version.imp(
            BaseConfig()
        ) as pypi_latest:
            async with pypi_latest(None, None) as ctx:
                results = await ctx.run({"package_json": self.INT_RESULT_JSON})
                self.assertEqual(results["version"], "0.1.0")

    async def test_002_package_url(self):
        async with pypi_package_url.imp(BaseConfig()) as pypi_url:
            async with pypi_url(None, None) as ctx:
                results = await ctx.run({"package_json": self.INT_RESULT_JSON})
                self.assertIn("insecure-package-0.1.0.tar.gz", results["url"])
