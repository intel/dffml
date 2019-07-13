import unittest

from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase

from dffml.source.mysql_source import MysqlSourceConfig, MysqlSource


class TestJSONSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return MysqlSource(
            MysqlSourceConfig(host="localhost", port=3306, user="root", password="some-password", db="dffml_source", repo_query="select count(*) from repo_data;", update_query="", repos_query="")
        )

    @unittest.skip("Labels not implemented")
    async def test_label(self):
        """
        Labels not implemented
        """
