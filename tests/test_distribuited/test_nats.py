import asyncio
import socketserver
import concurrent.futures
import subprocess

from dffml.util.asynctestcase import AsyncTestCase


from dffml.distribuited.orchestrator import NatsWorkerNode, NatsWorkerNodeConfig
from dffml import DataFlow
from dffml_feature_git.feature.operations import (
    check_if_valid_git_repository_URL,
)
from dffml.operation.output import GetSingle
from dffml.operation.db import (
    DatabaseQueryConfig,
    db_query_create_table,
)

import os
import tempfile
import asyncio

from dffml.distribuited.orchestrator import (
    NatsOrchestratorNode,
    NatsOrchestratorNodeConfig,
    NatsWorkerNode,
    NatsWorkerNodeConfig,
)
from dffml import DataFlow
from dffml_feature_git.feature.operations import (
    check_if_valid_git_repository_URL,
)
from dffml.operation.output import GetSingle
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig
from dffml.operation.db import (
    DatabaseQueryConfig,
    db_query_create_table,
)


class TestNatsOrchestrator(AsyncTestCase):
    async def setUp(self):
        self.nats_proc = subprocess.Popen(
            ["nats-server", "-p", "-1",],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

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
        self.nats_proc.terminate()

    async def test_run(self):
        server = self.server_addr
        subnode_1 = NatsWorkerNode(
            NatsWorkerNodeConfig(
                server=server,
                operations=[
                    check_if_valid_git_repository_URL.op,
                    db_query_create_table.op,
                ],
            )
        )

        fileno, database_name = tempfile.mkstemp(suffix=".db")
        os.close(fileno)
        sdb = SqliteDatabase(SqliteDatabaseConfig(filename=database_name))
        primarynode = NatsOrchestratorNode(
            NatsOrchestratorNodeConfig(
                server=server,
                dataflow=DataFlow(
                    operations={
                        "check_url": check_if_valid_git_repository_URL,
                        "dbq": db_query_create_table.op,
                    },
                    configs={"dbq": DatabaseQueryConfig(database=sdb)},
                ),
            )
        )

        async with subnode_1 as sn1:
            async with primarynode as pn:
                async with pn() as pnctx:
                    # Ensure subnode started new context
                    self.assertTrue(sn1.running_contexts)
                    sn1ctx = sn1.running_contexts[0]

                    self.assertEqual(
                        sn1ctx.operation_token,
                        {
                            "check_if_valid_git_repository_URL": 1,
                            "db_query_create_table": 1,
                        },
                    )

                    self.assertIn("check_url", sn1ctx.opimpctx.operations)
                    self.assertIn("dbq", sn1ctx.opimpctx.operations)
