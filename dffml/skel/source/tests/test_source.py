from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase

from REPLACE_IMPORT_PACKAGE_NAME.misc import MiscSourceConfig, MiscSource


class TestMiscSource(SourceTest, AsyncTestCase):
    async def setUpSource(self):
        return MiscSource(MiscSourceConfig(repos=[]))
