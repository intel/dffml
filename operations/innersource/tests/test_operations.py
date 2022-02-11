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


class TestOperations(AsyncTestCase):
    async def test_run(self):
        check = {"dffml": 42}
        async for ctx, results in run(
            DataFlow.auto(*OPIMPS),
            {
                "dffml": [
                    Input(
                        value=DFFML_ROOT_DIR.joinpath(".github", "workflows", "testing.yml").read_text(),
                        definition=parse_github_workflow.op.inputs["contents"],
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
