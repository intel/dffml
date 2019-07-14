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
                password="ABcd1234",
                db="dffml_source",
                table="repo_data",
                repo_query="",
                update_query="",
                repos_query="",
                model_columns="src_url feature_PetalLength feature_PetalWidth feature_SepalLength feature_SepalWidth prediction_confidence prediction_value",
            )
        )

    @unittest.skip("Labels not implemented")
    async def test_label(self):
        """
        Labels not implemented
        """
