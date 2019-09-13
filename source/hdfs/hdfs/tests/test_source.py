from dffml_source_hdfs.source import HDFSSourceConfig, HDFSSource

from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase
from dffml.source.csv import CSVSource, CSVSourceConfig


class TestHDFSSource(SourceTest, AsyncTestCase):
    async def setUpSource(self):
	print("\n \n HADOOP SOURCE RUNNING")
        return HDFSSource(
            HDFSSourceConfig(
                host="localhost",
                port="50070",
                user="hadoopuser",
                source=CSVSource(CSVSourceConfig(filename="sample_data.csv")),
                filepath="./home/hadoopuser/dffml-source/sample_data.csv",
            )
        )

    async def test_label(self):
        pass

