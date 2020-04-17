from dffml.source.ini import INISource, INISourceConfig
from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase


class TestINISource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return INISource(
            INISourceConfig(
                filename=self.testfile, allowempty=True, readwrite=True
            )
        )
