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
                repo_query="select * from repo_data where src_url=%s",
                update_query="insert into repo_data (`src_url`, `feature_PetalLength`, `feature_PetalWidth`, `feature_SepalLength`, `feature_SepalWidth`, `prediction_confidence`, `prediction_value`) values (%s,%s,%s,%s,%s,%s,%s) on duplicate key update src_url='%s', feature_PetalLength='%s', feature_PetalWidth='%s', feature_SepalLength='%s', feature_SepalWidth='%s', prediction_confidence='%s', prediction_value='%s'",
                repos_query="select * from repo_data",
                model_columns="src_url feature_PetalLength feature_PetalWidth feature_SepalLength feature_SepalWidth prediction_confidence prediction_value",
            )
        )

    @unittest.skip("Labels not implemented")
    async def test_label(self):
        """
        Labels not implemented
        """
