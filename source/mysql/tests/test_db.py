import socket
import contextlib
from unittest.mock import patch

from dffml.util.asynctestcase import AsyncTestCase

from dffml_source_mysql.db import MySQLDatabaseConfig, MySQLDatabase
from dffml_source_mysql.util.mysql_docker import mysql, DOCKER_ENV


class TestMySQLDatabase(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._exit_stack = contextlib.ExitStack()
        cls.exit_stack = cls._exit_stack.__enter__()
        cls.container_ip, cls.ca = cls.exit_stack.enter_context(mysql())
        cls.database_config = MySQLDatabaseConfig(
            host="mysql.unittest",
            port=3306,
            user=DOCKER_ENV["MYSQL_USER"],
            password=DOCKER_ENV["MYSQL_PASSWORD"],
            db=DOCKER_ENV["MYSQL_DATABASE"],
            ca=cls.ca,
        )
        # Make it so that when the client tries to connect to mysql.unittest the
        # address it get's back is the one for the container
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

    async def setUp(self):
        self.sdb = MySQLDatabase(self.database_config)
        self.table_name = "myTable"
        self.cols = {
            "key": "INT",
            "firstName": "VARCHAR(100)",
            "lastName": "VARCHAR(100)",
            "age": "INT",
        }
        self.data_dicts = [
            {"key": 10, "firstName": "John", "lastName": "Doe", "age": 16},
            {"key": 11, "firstName": "John", "lastName": "Miles", "age": 37},
            {"key": 12, "firstName": "Bill", "lastName": "Miles", "age": 40},
        ]

    async def test_0_create_table(self):
        async with self.sdb as db:
            async with db() as db_ctx:
                await db_ctx.create_table(self.table_name, self.cols)
                await db_ctx.conn.execute("show tables")
                results = await db_ctx.conn.fetchone()
                self.assertEqual(results["Tables_in_db"], self.table_name)

    async def test_1_set_get(self):
        async with self.sdb as db:
            async with db() as db_ctx:
                for data_dict in self.data_dicts:
                    await db_ctx.insert(self.table_name, data_dict)

                results = [row async for row in db_ctx.lookup(self.table_name)]
                self.assertEqual(results, self.data_dicts)

    async def test_2_update(self):
        data = {"age": 35}
        conditions = [
            [["firstName", "=", "John"], ["lastName", "=", "Miles"]],
            [["age", "<", "38"]],
        ]

        query_condition = [[["firstName", "=", "John"]]]

        async with self.sdb as db:
            async with db() as db_ctx:
                await db_ctx.update(self.table_name, data, conditions)
                results = [
                    row
                    async for row in db_ctx.lookup(
                        self.table_name, ["age"], query_condition
                    )
                ]

                self.assertEqual(results, [{"age": 35}, {"age": 35}])

    async def _test_3_remove(self):
        condition = [[["firstName", "=", "John"]]]
        async with self.sdb as db:
            async with db() as db_ctx:
                await db_ctx.remove(self.table_name, condition)
                results = [
                    row
                    async for row in db_ctx.lookup(
                        self.table_name, ["firstName"]
                    )
                ]
                self.assertEqual(results, [{"firstName": "Bill"}])
