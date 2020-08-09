import os
import asyncio
import sqlite3
import tempfile
import subprocess
import contextlib
from collections import defaultdict

from dffml.distributed.orchestrator import (
    NatsOrchestratorNode,
    NatsOrchestratorNodeConfig,
    NatsWorkerNode,
    NatsWorkerNodeConfig,
)

from dffml import DataFlow
from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.output import GetSingle
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig
from dffml.operation.db import (
    DatabaseQueryConfig,
    db_query_create_table,
    db_query_insert_or_update,
)

from tests.test_df import parse_line, add, mult


class TestNatsOrchestrator(AsyncTestCase):
    async def setUp(self):
        # - A worker node reads from a file containing input strings
        # - Input string are processed by another worker nodes(s)
        #   perfroming calc_string
        # - The result is stored in a database by another worker node
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS calculations (asString text PRIMARY KEY,value integer);"
        )
        self.cursor.execute("INSERT INTO calculations VALUES ('1+2' , 2)")

        self.nats_proc = subprocess.Popen(
            ["nats-server", "-p", "-1",],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        self.cursor.execute("SELECT * FROM calculations")
        rows = self.cursor.fetchall()
        ready = False
        listen_text = "Listening for client connections on "
        while not ready:
            line = self.nats_proc.stdout.readline().decode()
            if listen_text in line:
                line = line.strip().split(listen_text)
                self.server_addr = line[-1]
            if "Server is ready" in line:
                ready = True

    async def tearDown(self):
        self.conn.close()
        self.nats_proc.terminate()

    async def test_run(self):
        server = self.server_addr
        test_operations = [
            [parse_line.op,],
            [add.op, mult.op],
            [db_query_create_table.op, db_query_insert_or_update.op],
            [GetSingle.op],
        ]

        worker_nodes = [
            NatsWorkerNode(NatsWorkerNodeConfig(server, operations=ops))
            for ops in test_operations
        ]

        # Creating database
        fileno, database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)
        sdb = SqliteDatabase(SqliteDatabaseConfig(filename=":memory:"))

        primarynode = NatsOrchestratorNode(
            NatsOrchestratorNodeConfig(
                server=server,
                dataflow=DataFlow(
                    operations={
                        "parse_line": parse_line.op,
                        "add": add.op,
                        "mult": mult.op,
                        "db_create": db_query_create_table.op,
                        "db_insert": db_query_insert_or_update.op,
                        "get_single": GetSingle.imp.op,
                    },
                    configs={
                        "db_create": DatabaseQueryConfig(database=sdb),
                        "db_insert": DatabaseQueryConfig(database=sdb),
                    },
                ),
            )
        )

        async with contextlib.AsyncExitStack() as stack:
            worker_nodes = [
                await stack.enter_async_context(wnode)
                for wnode in worker_nodes
            ]
            async with primarynode as pn:
                async with pn() as pnctx:
                    tokens_assigned = defaultdict(lambda: [])
                    opimps_instantiated = []
                    # Itertate through all worker nodes and
                    # make sure contexts are instantiated, all
                    # the expected operation tokens/implementations
                    # have been set.
                    for wnode in worker_nodes:
                        self.assertTrue(wnode.running_contexts)
                        for snctx in wnode.running_contexts:
                            for (
                                op_name,
                                token,
                            ) in snctx.operation_token.items():
                                tokens_assigned[op_name].append(token)
                            opimps_instantiated.extend(
                                snctx.opimpctx.operations.keys()
                            )

                    print(tokens_assigned)
                    print(opimps_instantiated)
