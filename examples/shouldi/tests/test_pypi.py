from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.pypi import pypi_package_json
from shouldi.pypi import pypi_latest_package_version

from pathlib import Path
import json

class TestPyPiPackageJson(AsyncTestCase):
    async def test_run(self):
        async with pypi_package_json.imp(
            BaseConfig()
            ) as pypi_package:
                async with pypi_package(None, None) as ctx:
                    results = await ctx.run({"package": "insecure-package"})
                    self.assertIs(type(results["response_json"]), dict)
                    file_path = Path("response.json")
                    file_path.write_text(json.dumps(results["response_json"]))

class TestPyPiLatestPackageVersion(AsyncTestCase):
    #async def setup(self):
    #    file_path = Path("response.json")
    #    int_result_json = json.loads(file_path.read_text())
    #    print(result_json)
    async def test_run(self):
        async with pypi_latest_package_version.imp(
            BaseConfig()
        ) as pypi_latest:
            async with pypi_latest(None, None) as ctx:
                int_result_json = {"info": {"version": "0.1.0"}}
                results = await ctx.run({"package_json": int_result_json})
                self.assertEqual(results["version"], "0.1.0")
