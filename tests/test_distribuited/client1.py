import asyncio

from dffml.distribuited.orchestrator import NatsSubNode, NatsSubNodeConfig
from dffml import DataFlow
from dffml_feature_git.feature.operations import (
    check_if_valid_git_repository_URL,
)
from dffml.operation.output import GetSingle
from dffml.operation.db import (
    DatabaseQueryConfig,
    db_query_create_table,
)



async def main():
    server = "0.0.0.0:4222"
    sn1 = NatsSubNode(
        NatsSubNodeConfig(
            server=server,
            operations=[check_if_valid_git_repository_URL.op,db_query_create_table.op]
        )
    )

    async with sn1() as sn:
        pass


asyncio.run(main())
