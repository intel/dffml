import unittest

from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase

from .custom_sqlite import CustomSQLiteSourceConfig, CustomSQLiteSource


class TestJSONSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return CustomSQLiteSource(
            CustomSQLiteSourceConfig(filename=self.testfile)
        )

    @unittest.skip("Labels not implemented")
    async def test_label(self):
        """
        Labels not implemented
        """
