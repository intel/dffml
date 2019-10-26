import sys

from dffml.df.types import Input, DataFlow
from dffml.df.base import operation_in, opimp_in, Operation
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from REPLACE_IMPORT_PACKAGE_NAME.operations import *

OPIMPS = opimp_in(sys.modules[__name__])


class TestOperations(AsyncTestCase):
    async def test_run(self):
        dataflow = DataFlow.auto(*OPIMPS)
        calc_strings_check = {"add 40 and 2": 42, "multiply 42 and 10": 420}
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(
                    {
                        to_calc: [
                            Input(
                                value=to_calc,
                                definition=calc_parse_line.op.inputs["line"],
                            ),
                            Input(
                                value=[calc_add.op.outputs["sum"].name],
                                definition=GetSingle.op.inputs["spec"],
                            ),
                        ]
                        for to_calc in calc_strings_check.keys()
                    }
                ):
                    ctx_str = (await ctx.handle()).as_string()
                    self.assertEqual(
                        calc_strings_check[ctx_str],
                        results[calc_add.op.outputs["sum"].name],
                    )
