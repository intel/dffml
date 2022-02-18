import sys
import pathlib
import itertools

from dffml.high_level.dataflow import run
from dffml.df.types import Input, DataFlow
from dffml.df.base import opimp_in
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operations_innersource.operations import *

OPIMPS = opimp_in(sys.modules[__name__])

DFFML_ROOT_DIR = pathlib.Path(__file__).parents[3]

DATAFLOW = DataFlow.auto(
    *OPIMPS,
)


class TestOperations(AsyncTestCase):
    async def test_run(self):
        check = {
            "dffml": {
                github_workflow_present.op.outputs["result"].name: True
            },
        }
        async for ctx, results in run(
            DATAFLOW,
            {
                "dffml": [
                    Input(
                        value=github_workflow_present.op.inputs["repo"].spec(
                            directory=DFFML_ROOT_DIR,
                        ),
                        definition=github_workflow_present.op.inputs["repo"],
                    ),
                    Input(
                        value=list(itertools.chain(*[
                            [
                                definition.name
                                for definition in opimp.op.outputs.values()
                            ]
                            for opimp in OPIMPS
                            if opimp.op.name != "get_single"
                        ])),
                        definition=GetSingle.op.inputs["spec"],
                    ),
                ]
            }
        ):
            ctx_str = (await ctx.handle()).as_string()
            self.assertEqual(
                check[ctx_str],
                results,
            )
