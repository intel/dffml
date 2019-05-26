from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase

from .custom_sqlite import CustomSQLiteSourceConfig, CustomSQLiteSource


class TestJSONSource(SourceTest, AsyncTestCase):
    async def setUpFile(self, fileobj):
        return
        fileobj.write(b"{}")
        fileobj.seek(0)

    async def setUpSource(self, fileobj):
        return CustomSQLiteSource(
            CustomSQLiteSourceConfig(filename=fileobj.name)
        )
