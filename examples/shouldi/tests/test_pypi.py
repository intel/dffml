import json
import os
import shutil
import tempfile
from pathlib import Path

from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.pypi import pypi_package_json
from shouldi.pypi import pypi_latest_package_version
from shouldi.pypi import pypi_package_url
from shouldi.pypi import pypi_package_contents
from shouldi.pypi import cleanup_pypi_package


class TestPyPiOperations(AsyncTestCase):
    PACKAGE = "insecure-package"
    INT_RESULT_JSON = {}
    PACKAGE_URL = None

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
                self.PACKAGE_URL = results["url"]

    async def test_003_package_contents(self):
        PACKAGE_URL = "https://files.pythonhosted.org/packages/dd/b7/b7318693b356d0e0ba566fb22b72a349a10337880c254e5e7e9f24f4f9b3/insecure-package-0.1.0.tar.gz"
        async with pypi_package_contents.imp(BaseConfig()) as pypi_cont:
            async with pypi_cont(None, None) as ctx:
                results = await ctx.run({"package_url": PACKAGE_URL})
                no_files = os.listdir(results["directory"])
                self.assertGreater(len(no_files), 0)
                shutil.rmtree(results["directory"])

    async def test_004_cleanup_package(self):
        temp_dir = tempfile.mkdtemp(prefix="temp-")
        async with cleanup_pypi_package.imp(BaseConfig()) as cleanup_cont:
            async with cleanup_cont(None, None) as ctx:
                results = await ctx.run({"directory": temp_dir})
                self.assertDictEqual(results, {})
