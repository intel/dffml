import random

from dffml.df.types import Operation, Input, DataFlow
from dffml.df.base import BaseConfig, StringInputSetContext
from dffml.df.memory import (
    MemoryOrchestrator,
    MemoryInputSet,
    MemoryInputSetConfig,
)

from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from dffml_feature_auth.feature.operations import Scrypt

OPIMPS = [Scrypt, GetSingle.imp]
OPERATIONS = [Scrypt.op, GetSingle.imp.op]


class TestRunner(AsyncTestCase):
    async def test_run(self):
        dataflow = DataFlow.auto(*OPIMPS)
        passwords = [str(random.random()) for _ in range(0, 20)]

        # Orchestrate the running of these operations
        async with MemoryOrchestrator.withconfig({}) as orchestrator:

            definitions = Operation.definitions(*OPERATIONS)

            passwords = [
                Input(
                    value=password,
                    definition=definitions["UnhashedPassword"],
                    parents=None,
                )
                for password in passwords
            ]

            output_spec = Input(
                value=["ScryptPassword"],
                definition=definitions["get_single_spec"],
                parents=None,
            )

            async with orchestrator(dataflow) as octx:
                try:
                    async for _ctx, results in octx.run(
                        {
                            password.value: [password, output_spec]
                            for password in passwords
                        }
                    ):
                        self.assertTrue(results)
                except AttributeError as error:
                    raise
