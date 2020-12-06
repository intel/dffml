import unittest

from dffml import AsyncTestCase, FileSourceTest

from dffml_source_sqlite.misc import (
    CustomSQLiteSourceConfig,
    CustomSQLiteSource,
)


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
