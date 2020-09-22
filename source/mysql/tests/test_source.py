import socket
import inspect
import unittest
import contextlib
from unittest.mock import patch

from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase

from dffml_source_mysql.source import MySQLSourceConfig, MySQLSource

from dffml_source_mysql.util.mysql_docker import mysql, DOCKER_ENV


class TestMySQLSource(AsyncTestCase, SourceTest):

    SQL_SETUP = """
CREATE TABLE IF NOT EXISTS `record_data` (
  `key` varchar(100) NOT NULL,
  `PetalLength` float DEFAULT NULL,
  `PetalWidth` float DEFAULT NULL,
  `SepalLength` float DEFAULT NULL,
  `SepalWidth` float DEFAULT NULL,
  `flower_type` varchar(100) DEFAULT NULL,
  `flower_confidence` float DEFAULT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._exit_stack = contextlib.ExitStack()
        cls.exit_stack = cls._exit_stack.__enter__()
        cls.container_ip, cls.ca = cls.exit_stack.enter_context(mysql())
        cls.source_config = MySQLSourceConfig(
            host="mysql.unittest",
            port=3306,
            user=DOCKER_ENV["MYSQL_USER"],
            password=DOCKER_ENV["MYSQL_PASSWORD"],
            db=DOCKER_ENV["MYSQL_DATABASE"],
            key="key",
            features={
                k: k
                for k in [
                    "PetalLength",
                    "PetalWidth",
                    "SepalLength",
                    "SepalWidth",
                ]
            },
            predictions={"target_name": ("flower_type", "flower_confidence")},
            ca=cls.ca,
            init=cls.SQL_SETUP,
            record="SELECT * FROM record_data WHERE `key`=%s",
            records="SELECT * FROM record_data",
            update=inspect.cleandoc(
                """
                INSERT INTO record_data
                (
                    `key`,
                    `PetalLength`,
                    `PetalWidth`,
                    `SepalLength`,
                    `SepalWidth`,
                    `flower_type`,
                    `flower_confidence`
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE
                    `PetalLength`=%s,
                    `PetalWidth`=%s,
                    `SepalLength`=%s,
                    `SepalWidth`=%s,
                    `flower_type`=%s,
                    `flower_confidence`=%s
                """
            ),
        )
        # Make it so that when the client tries to connect to mysql.unittest the
        # address it gets back is the one for the container
        cls.exit_stack.enter_context(
            patch(
                "socket.getaddrinfo",
                return_value=[
                    (
                        socket.AF_INET,
                        socket.SOCK_STREAM,
                        6,
                        "",
                        (cls.container_ip, 3306),
                    )
                ],
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._exit_stack.__exit__(None, None, None)

    async def setUpSource(self):
        return MySQLSource(self.source_config)
