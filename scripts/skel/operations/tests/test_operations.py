import sys

from dffml.df.types import Input
from dffml.df.base import (
    operation_in,
    opimp_in,
    Operation,
    BaseConfig,
    StringInputSetContext,
)
from dffml.df.memory import (
    MemoryOrchestrator,
    MemoryInputSet,
    MemoryInputSetConfig,
)
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operations_operations_name.operations import *

OPERATIONS = operation_in(sys.modules[__name__])
OPIMPS = opimp_in(sys.modules[__name__])


class TestOperations(AsyncTestCase):
    async def test_run(self):
        calc_strings_check = {"add 40 and 2": 42, "multiply 42 and 10": 420}

        # Orchestrate the running of these operations
        async with MemoryOrchestrator.basic_config(
            operations=OPERATIONS,
            opimps={
                imp.op.name: imp
                for imp in [Imp(BaseConfig()) for Imp in OPIMPS]
            },
        ) as orchestrator:

            definitions = Operation.definitions(*OPERATIONS)

            calc_strings = {
                to_calc: Input(
                    value=to_calc,
                    definition=definitions["calc_string"],
                    parents=False,
                )
                for to_calc in calc_strings_check.keys()
            }

            get_single_spec = Input(
                value=["result"],
                definition=definitions["get_single_spec"],
                parents=False,
            )

            async with orchestrator() as octx:
                # Add our inputs to the input network with the context being the URL
                for to_calc in calc_strings_check.keys():
                    await octx.ictx.add(
                        MemoryInputSet(
                            MemoryInputSetConfig(
                                ctx=StringInputSetContext(to_calc),
                                inputs=[calc_strings[to_calc]]
                                + [get_single_spec],
                            )
                        )
                    )

                async for ctx, results in octx.run_operations(strict=True):
                    ctx_str = (await ctx.handle()).as_string()
                    self.assertEqual(
                        calc_strings_check[ctx_str],
                        results["get_single"]["result"],
                    )
