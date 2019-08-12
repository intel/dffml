import os
import json
import random
import unittest
import subprocess
import contextlib

from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase

from dffml_source_mysql.source import MysqlSourceConfig, MysqlSource

from dffml_source_mysql.util.mysql_docker import mysql, DOCKER_ENV


class TestMySQLSource(AsyncTestCase, SourceTest):

    SQL_SETUP = """
DROP TABLE IF EXISTS `repo_data`;
CREATE TABLE `repo_data` (
  `src_url` varchar(100) NOT NULL,
  `feature_PetalLength` float DEFAULT NULL,
  `feature_PetalWidth` float DEFAULT NULL,
  `feature_SepalLength` float DEFAULT NULL,
  `feature_SepalWidth` float DEFAULT NULL,
  `prediction_confidence` float DEFAULT NULL,
  `prediction_value` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`src_url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._exit_stack = contextlib.ExitStack()
        cls.exit_stack = cls._exit_stack.__enter__()
        cls.container_ip = cls.exit_stack.enter_context(
            mysql(sql_setup=cls.SQL_SETUP)
        )
        cls.source_config = MysqlSourceConfig(
            host=cls.container_ip,
            port=3306,
            user=DOCKER_ENV["MYSQL_USER"],
            password=DOCKER_ENV["MYSQL_PASSWORD"],
            db=DOCKER_ENV["MYSQL_DATABASE"],
            repo_query="select * from repo_data where src_url=%s",
            update_query="""insert into repo_data (`src_url`, `feature_PetalLength`, `feature_PetalWidth`, `feature_SepalLength`, `feature_SepalWidth`, `prediction_confidence`, `prediction_value`) values (%s,%s,%s,%s,%s,%s,%s) on duplicate key update src_url=%s, feature_PetalLength=%s, feature_PetalWidth=%s, feature_SepalLength=%s, feature_SepalWidth=%s, prediction_confidence=%s, prediction_value=%s""",
            repos_query="select * from repo_data",
            model_columns="src_url feature_PetalLength feature_PetalWidth feature_SepalLength feature_SepalWidth prediction_confidence prediction_value",
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._exit_stack.__exit__(None, None, None)

    async def setUpSource(self):
        return MysqlSource(self.source_config)

    @unittest.skip("Labels not implemented")
    async def test_label(self):
        """
        Labels not implemented
        """
