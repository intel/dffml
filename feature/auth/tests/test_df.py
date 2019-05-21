import random

from dffml.df.types import Operation, Input
from dffml.df.base import BaseConfig, \
                          StringInputSetContext
from dffml.df.memory import MemoryOrchestrator, \
                            MemoryInputSet, \
                            MemoryInputSetConfig

from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from dffml_feature_auth.feature.operations import Scrypt

OPIMPS = [Scrypt, GetSingle.imp]
OPERATIONS = [Scrypt.op, GetSingle.imp.op]

class TestRunner(AsyncTestCase):

    async def test_run(self):
        passwords = [
            str(random.random()) for _ in range(0, 20)
            ]

        # Orchestrate the running of these operations
        async with MemoryOrchestrator.basic_config(
                operations=OPERATIONS,
                opimps={imp.op.name: imp \
                  for imp in \
                  [Imp(BaseConfig()) for Imp in OPIMPS]}
                ) as orchestrator:

            definitions = Operation.definitions(*OPERATIONS)

            passwords = [Input(value=password,
                               definition=definitions['UnhashedPassword'],
                               parents=False) for password in passwords]

            output_spec = Input(value=['ScryptPassword'],
                                definition=definitions['get_single_spec'],
                                parents=False)

            async with orchestrator() as octx:
                # Add our inputs to the input network with the context being the URL
                for password in passwords:
                    await octx.ictx.add(
                        MemoryInputSet(
                            MemoryInputSetConfig(
                                ctx=StringInputSetContext(password.value),
                                inputs=[password, output_spec]
                            )
                        )
                    )
                try:
                    async for _ctx, results in octx.run_operations(strict=True):
                        self.assertTrue(results)
                except AttributeError as error:
                    if "module 'hashlib' has no attribute 'scrypt'" \
                            in str(error):
                        return
                    raise
