import unittest

from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase

from dffml.source.mysql_source import MysqlSourceConfig, MysqlSource


class TestMySQLSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return MysqlSource(
            MysqlSourceConfig(
                host="localhost",
                port=3306,
                user="root",
                password="some-password",
                db="dffml_source",
                repo_query="select src_url, feature_a, feature_b FROM repo_data WHERE src_url=%s",
                update_query="",
                repos_query="",
            )
        )

    @unittest.skip("Labels not implemented")
    async def test_label(self):
        """
        Labels not implemented
        """

    @unittest.skip("Update not implemented")
    async def test_update(self):
        """
        Update not implemented
        """
