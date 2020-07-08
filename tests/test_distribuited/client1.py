import asyncio

from dffml.distribuited.orchestrator import NatsSubNode,NatsSubNodeConfig
from dffml import DataFlow
from dffml_feature_git.feature.operations import check_if_valid_git_repository_URL
from dffml.operation.output import GetSingle

async def main():
    server = "0.0.0.0:4222"
    cluster = "test-cluster"
    sn1 = NatsSubNode(
        NatsSubNodeConfig(
            server= server,
            cluster= cluster,
            operations = [GetSingle.op]
            )
    )

    async with sn1() as snctx:
        print(snctx)

asyncio.run(main())