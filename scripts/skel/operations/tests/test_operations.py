import sys

from dffml.df.types import Input
from dffml.df.base import operation_in, opimp_in, Operation
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operations_operations_name.operations import *

OPIMPS = opimp_in(sys.modules[__name__])


class TestOperations(AsyncTestCase):
    async def test_run(self):
        calc_strings_check = {"add 40 and 2": 42, "multiply 42 and 10": 420}

        async with MemoryOrchestrator.basic_config(*OPIMPS) as orchestrator:
            async with orchestrator() as octx:
                for to_calc in calc_strings_check.keys():
                    await octx.ictx.sadd(
                        to_calc,
                        Input(
                            value=to_calc,
                            definition=calc_parse_line.op.inputs["line"],
                        ),
                        Input(
                            value=[calc_add.op.outputs["sum"].name],
                            definition=GetSingle.op.inputs["spec"],
                        ),
                    )

                async for ctx, results in octx.run_operations():
                    ctx_str = (await ctx.handle()).as_string()
                    self.assertEqual(
                        calc_strings_check[ctx_str],
                        results[GetSingle.op.name][
                            calc_add.op.outputs["sum"].name
                        ],
                    )
