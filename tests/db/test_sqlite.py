import os
import tempfile

from dffml.util.asynctestcase import AsyncTestCase
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig


class TestSqlDatabase(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        fileno, cls.database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.database_name)

    async def setUp(self):
        self.sdb = SqliteDatabase(
            SqliteDatabaseConfig(filename=self.database_name)
        )
        await self.sdb.__aenter__()
        self.table_name = "myTable"
        self.cols = {
            "key": "INTEGER NOT NULL PRIMARY KEY",
            "firstName": "text",
            "lastName": "text",
            "age": "real",
        }
        self.data_dicts = [
            {"key": 10, "firstName": "John", "lastName": "Doe", "age": 16},
            {"key": 11, "firstName": "John", "lastName": "Miles", "age": 37},
            {"key": 12, "firstName": "Bill", "lastName": "Miles", "age": 40},
        ]

    async def tearDown(self):
        await self.sdb.__aexit__(None, None, None)

    async def test_0_create_table(self):
        async with self.sdb() as db_ctx:
            await db_ctx.create_table(self.table_name, self.cols)
            query = (
                "SELECT count(name) FROM sqlite_master "
                + " WHERE type='table' and name='myTable' "
            )
            db_ctx.parent.cursor.execute(query)
            results = db_ctx.parent.cursor.fetchone()
            self.assertEqual(results[0], 1)

    async def test_1_set_get(self):

        async with self.sdb() as db_ctx:
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

        async with self.sdb() as db_ctx:
            await db_ctx.update(self.table_name, data, conditions)
            results = [
                row
                async for row in db_ctx.lookup(
                    self.table_name, ["age"], query_condition
                )
            ]

            self.assertEqual(results, [{"age": 35}, {"age": 35}])

    async def test_3_remove(self):
        condition = [[["firstName", "=", "John"]]]
        async with self.sdb() as db_ctx:
            await db_ctx.remove(self.table_name, condition)
            results = [
                row
                async for row in db_ctx.lookup(self.table_name, ["firstName"])
            ]
            self.assertEqual(results, [{"firstName": "Bill"}])

    async def test_4_insert_or_update(self):
        data = {"key": 12, "firstName": "Biller"}
        expected = [
            {
                "key": 12,
                "firstName": "Biller",
                "lastName": "Miles",
                "age": 40.0,
            }
        ]
        async with self.sdb() as db_ctx:
            await db_ctx.insert_or_update(self.table_name, data)
            results = [row async for row in db_ctx.lookup(self.table_name)]
            self.assertEqual(results, expected)
