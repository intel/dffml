import unittest

from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase

from .custom_sqlite import CustomSQLiteSourceConfig, CustomSQLiteSource


class TestCustomSQliteSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return CustomSQLiteSource(
            CustomSQLiteSourceConfig(filename=self.testfile)
        )

    @unittest.skip("tags not implemented")
    async def test_tag(self):
        """
        tags not implemented
        """
