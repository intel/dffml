import os
import tempfile

from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.db import (
    DatabaseQueryConfig,
    db_query_create_table,
    db_query_insert,
    db_query_lookup,
)
from dffml.df.types import DataFlow, Input
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator


class TestSqliteQuery(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fileno, cls.database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)
        cls.sdb = SqliteDatabase(
            SqliteDatabaseConfig(filename=cls.database_name)
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        os.unlink(cls.database_name)

    def setUp(self):
        self.table_name = "myTable"
        self.cols = {
            "key": "real",
            "firstName": "text",
            "lastName": "text",
            "age": "integer",
        }
        self.data_dicts = [
            {"key": 10, "firstName": "John", "lastName": "Doe", "age": 16},
            {"key": 11, "firstName": "John", "lastName": "Miles", "age": 37},
            {"key": 12, "firstName": "Bill", "lastName": "Miles", "age": 40},
        ]

    def _create_dataflow_with_op(self, query_op, seed=[]):
        return DataFlow(
            operations={
                "db_query": query_op.op,
                "get_single": GetSingle.imp.op,
            },
            configs={"db_query": DatabaseQueryConfig(database=self.sdb)},
            seed=seed,
            implementations={query_op.op.name: query_op.imp},
        )

    async def test_0_create(self):

        df = self._create_dataflow_with_op(db_query_create_table)
        test_inputs = {
            "create": {"table_name": self.table_name, "cols": self.cols}
        }

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(df) as octx:
                async for _ctx, results in octx.run(
                    {
                        test_ctx: [
                            Input(
                                value=val,
                                definition=db_query_create_table.op.inputs[
                                    key
                                ],
                            )
                            for key, val in test_val.items()
                        ]
                        for test_ctx, test_val in test_inputs.items()
                    }
                ):
                    pass

            async with self.sdb as db:
                async with db() as db_ctx:
                    query = (
                        "SELECT count(name) FROM sqlite_master "
                        + f" WHERE type='table' and name='{self.table_name}' "
                    )
                    db_ctx.parent.cursor.execute(query)
                    results = db_ctx.parent.cursor.fetchone()
                    self.assertEqual(results["count(name)"], 1)

    async def test_1_insert(self):

        df = self._create_dataflow_with_op(db_query_insert)
        for _data in self.data_dicts:
            test_inputs = {
                "insert": {"table_name": self.table_name, "data": _data}
            }

            async with MemoryOrchestrator.withconfig({}) as orchestrator:
                async with orchestrator(df) as octx:
                    async for _ctx, results in octx.run(
                        {
                            test_ctx: [
                                Input(
                                    value=val,
                                    definition=db_query_insert.op.inputs[key],
                                )
                                for key, val in test_val.items()
                            ]
                            for test_ctx, test_val in test_inputs.items()
                        }
                    ):
                        continue

        async with self.sdb as db:
            async with db() as db_ctx:
                query = f"SELECT * FROM {self.table_name}"
                db_ctx.parent.cursor.execute(query)
                rows = db_ctx.parent.cursor.fetchall()
                self.assertEqual(self.data_dicts, list(map(dict, rows)))

    async def test_2_lookup(self):
        seed = [
            Input(
                value=[db_query_lookup.op.outputs["lookups"].name],
                definition=GetSingle.op.inputs["spec"],
            )
        ]
        df = self._create_dataflow_with_op(db_query_lookup, seed=seed)
        test_inputs = {
            "lookup": {
                "table_name": self.table_name,
                "cols": [],
                "conditions": [],
            }
        }

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(df) as octx:
                async for _ctx, results in octx.run(
                    {
                        test_ctx: [
                            Input(
                                value=val,
                                definition=db_query_lookup.op.inputs[key],
                            )
                            for key, val in test_val.items()
                        ]
                        for test_ctx, test_val in test_inputs.items()
                    }
                ):
                    self.assertIn("query_lookups", results)
                    results = results["query_lookups"]
                    self.assertEqual(self.data_dicts, results)
