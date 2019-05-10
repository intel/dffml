import json
import random

from dffml.df import *
from dffml.operation.output import GetSingle
from dffml_feature_auth.feature.operations import *

from dffml.util.asynctestcase import AsyncTestCase

OPWRAPED = opwraped_in(sys.modules[__name__])
OPERATIONS = operation_in(sys.modules[__name__]) + \
             list(map(lambda item: item.op, OPWRAPED))
OPIMPS = opimp_in(sys.modules[__name__]) + \
         list(map(lambda item: item.imp, OPWRAPED))

class TestRunner(AsyncTestCase):

    async def test_run(self):
        linker = Linker()
        exported = linker.export(*OPERATIONS)
        definitions, operations, _outputs = linker.resolve(exported)

        passwords = [
            str(random.random()) for _ in range(0, 20)
            ]
        passwords = [Input(value=password,
                           definition=definitions['UnhashedPassword'],
                           parents=False) for password in passwords]

        output_spec = Input(value=['ScryptPassword'],
                            definition=definitions['get_single_spec'],
                            parents=False)

        opimps = {imp.op.name: imp \
                  for imp in \
                  [Imp(BaseConfig()) for Imp in OPIMPS]}

        dff = DataFlowFacilitator(
            input_network = MemoryInputNetwork(BaseConfig()),
            operation_network = MemoryOperationNetwork(
                MemoryOperationNetworkConfig(
                    operations=list(operations.values())
                )
            ),
            lock_network = MemoryLockNetwork(BaseConfig()),
            rchecker = MemoryRedundancyChecker(
                BaseRedundancyCheckerConfig(
                    key_value_store=MemoryKeyValueStore(BaseConfig())
                )
            ),
            opimp_network = MemoryOperationImplementationNetwork(
                MemoryOperationImplementationNetworkConfig(
                    operations=opimps
                )
            ),
            orchestrator = MemoryOrchestrator(BaseConfig())
        )


        # Orchestrate the running of these operations
        async with dff as dff:
            async with dff() as dffctx:
                # Add our inputs to the input network with the context being the URL
                for password in passwords:
                    await dffctx.ictx.add(
                        MemoryInputSet(
                            MemoryInputSetConfig(
                                ctx=StringInputSetContext(password.value),
                                inputs=[password, output_spec]
                            )
                        )
                    )
                async for ctx, results in dffctx.evaluate(strict=True):
                    print()
                    print((await ctx.handle()).as_string(),
                          json.dumps(results, sort_keys=True,
                                     indent=4, separators=(',', ':')))
                    print()
                    # self.assertTrue(results)
