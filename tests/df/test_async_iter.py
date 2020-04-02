from dffml.df.types import DataFlow, Input, Definition
from dffml.df.base import op
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.mapping import MAPPING


CountStart = Definition(name="count_start",primitive="int")
Count = Definition(name="count",primitive="int")
Number = Definition(name="number",primitive="int")


@op(inputs={"count_start": CountStart}, outputs={"count": Count})
async def counter(count_start):
    for i in range(count_start,count_start+5):
        yield {"count":i}

@op(inputs={}, outputs={"count": Count})
async def counter_auto_start():
    for i in range(5):
        yield {"count":i}


@op(inputs={"number_in": Count}, outputs={"number_out": Number})
def echo_num(number_in:int):
    print(f"{number_in}")
    return {"number_out":number_in}


class TestAsyncIter(AsyncTestCase):
    async def test_gen_with_input(self):
        test_dataflow = DataFlow(
            operations={
                "counter": counter.op,
                "get_single": GetSingle.imp.op,
                "echo_num":echo_num.op
            },
            seed=[
                Input(
                    value=[echo_num.op.outputs["number_out"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ],
            implementations={
                    counter.op.name: counter.imp,
                    echo_num.op.name : echo_num.imp
                            },
        )
        test_inputs = {"TestCount": [Input(value=1, definition=CountStart),]}
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(test_dataflow) as octx:
                async for ctx_str, results in octx.run(test_inputs):
                    pass
    async def test_gen_auto_start(self):
        test_dataflow = DataFlow(
            operations={
                "counter": counter_auto_start.op,
                "get_single": GetSingle.imp.op,
                "echo_num":echo_num.op
            },
            seed=[
                Input(
                    value=[echo_num.op.outputs["number_out"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ],
            implementations={
                    counter_auto_start.op.name: counter_auto_start.imp,
                    echo_num.op.name : echo_num.imp
                            },
        )
        test_inputs = {"TestCountAutoStart": [Input(value=1, definition=CountStart),]}
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(test_dataflow) as octx:
                async for ctx_str, results in octx.run(test_inputs):
                    print(f"results : {results}")
    
