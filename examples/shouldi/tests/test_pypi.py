from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.pypi import pypi_package_json
from shouldi.pypi import pypi_latest_package_version
from shouldi.pypi import pypi_package_url

from pathlib import Path
import json


class TestPyPiPackageJson(AsyncTestCase):
    async def test_run(self):
        async with pypi_package_json.imp(BaseConfig()) as pypi_package:
            async with pypi_package(None, None) as ctx:
                results = await ctx.run({"package": "insecure-package"})
                self.assertIs(type(results["response_json"]), dict)
                file_path = Path("response.json")
                file_path.write_text(json.dumps(results["response_json"]))


class TestPyPiLatestPackageVersion(AsyncTestCase):
    async def test_run(self):
        async with pypi_latest_package_version.imp(
            BaseConfig()
        ) as pypi_latest:
            async with pypi_latest(None, None) as ctx:
                file_path = Path("response.json")
                int_result_json = json.loads(file_path.read_text())
                results = await ctx.run({"package_json": int_result_json})
                self.assertEqual(results["version"], "0.1.0")


class TestPyPiPackageUrl(AsyncTestCase):
    async def test_run(self):
        async with pypi_package_url.imp(BaseConfig()) as pypi_url:
            async with pypi_url(None, None) as ctx:
                file_path = Path("response.json")
                int_result_json = json.loads(file_path.read_text())
                results = await ctx.run({"package_json": int_result_json})
                self.assertIn("insecure-package-0.1.0.tar.gz", results["url"])
