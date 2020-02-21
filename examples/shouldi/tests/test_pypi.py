import os
import shutil
import tempfile

from dffml.util.asynctestcase import AsyncTestCase

from shouldi.pypi import pypi_package_json
from shouldi.pypi import pypi_latest_package_version
from shouldi.pypi import pypi_package_url
from shouldi.pypi import pypi_package_contents
from shouldi.pypi import cleanup_pypi_package


class TestPyPiOperations(AsyncTestCase):
    PACKAGE = {"name": "insecure-package"}
    INT_RESULT_JSON = {}

    async def test_000_package_json(self):
        # Call the .test method created by the @op decorator. This sets up the
        # aiohttp.ClientSession object.
        results = await pypi_package_json.test(package=self.PACKAGE["name"])
        self.assertIs(type(results["response_json"]), dict)
        self.INT_RESULT_JSON.update(results["response_json"])

    async def test_001_package_version(self):
        results = await pypi_latest_package_version(self.INT_RESULT_JSON)
        self.assertEqual(results["version"], "0.1.0")

    async def test_002_package_url(self):
        results = await pypi_package_url(self.INT_RESULT_JSON)
        self.assertIn("insecure-package-0.1.0.tar.gz", results["url"])
        self.PACKAGE.update(results)

    async def test_003_package_contents(self):
        try:
            results = await pypi_package_contents.test(url=self.PACKAGE["url"])
            no_files = os.listdir(results["directory"])
            self.assertGreater(len(no_files), 0)
        finally:
            shutil.rmtree(results["directory"])

    async def test_004_cleanup_package(self):
        tempdir = tempfile.mkdtemp()
        await cleanup_pypi_package(tempdir)
        self.assertFalse(os.path.isdir(tempdir))
