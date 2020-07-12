import os
import tempfile
import asyncio

from dffml.distribuited.orchestrator import (
    NatsPrimaryNode,
    NatsPrimaryNodeConfig,
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



async def main():
    server = "0.0.0.0:4222"
    fileno, database_name = tempfile.mkstemp(suffix=".db")
    os.close(fileno)
    sdb = SqliteDatabase(
            SqliteDatabaseConfig(filename=database_name)
        )
    primary_node = NatsPrimaryNode(
        NatsPrimaryNodeConfig(
            server=server,
            dataflow=DataFlow(
                operations = {
                    "check_url": check_if_valid_git_repository_URL,
                    "dbq": db_query_create_table.op,
                },
                configs={
                    "dbq": DatabaseQueryConfig(database=sdb)
                }
            )
        )
    )

    async with primary_node as pn:
        async with pn() as pnctx:
            pass


asyncio.run(main())
