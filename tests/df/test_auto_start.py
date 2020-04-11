from dffml.df.base import op
from dffml.df.types import DataFlow, Input, Definition
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase
from dffml.df.memory import MemoryOrchestrator

STRING = Definition(name="string", primitive="str")


@op(inputs={}, outputs={"string_out": STRING})
async def announce():
    return {"string_out": "EXISTS"}


class TestAutoStart(AsyncTestCase):
    async def setUp(self):
        dataflow = DataFlow(
            operations={
                "announce": announce.op,
                "get_single": GetSingle.imp.op,
            },
            seed=[
                Input(
                    value=[announce.op.outputs["string_out"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ],
            implementations={announce.op.name: announce.imp},
        )

        self.dataflow = dataflow

    async def test_auto_start(self):
        test_inputs = {"testStart": []}
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(self.dataflow) as octx:
                async for ctx_str, results in octx.run(test_inputs):
                    self.assertIn("string", results)
                    self.assertEqual("EXISTS", results["string"])
