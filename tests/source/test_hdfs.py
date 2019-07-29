from dffml.source.hdfs_source import HDFSSourceConfig, HDFSSource

from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase

class TestHDFSSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return HDFSSource(HDFSSourceConfig(host="localhost", port="50070", user="hadoopuser", source="CSVSource", filepath="./home/hadoopuser/dffml-source/sample_data.csv"))

    async def test_label(self):
        pass

    async def test_update(self):
        source = await self.setUpSource()
        async with source as testSource:
            # Open and confirm we saved and loaded correctly
            async with testSource() as sourceContext:
                repo = await sourceContext.__aenter__()
        pass
