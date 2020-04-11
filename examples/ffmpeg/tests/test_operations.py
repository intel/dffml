import sys

from dffml.df.types import Input, DataFlow
from dffml.df.base import opimp_in
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from ffmpeg.operations import convert_to_gif




class TestOperations(AsyncTestCase):
    async def test_run(self):
        dataflow = DataFlow.auto(convert_to_gif)
        test_inputs = {
            "Test": [
                Input(value="input.mp4", definition=convert_to_gif.op.inputs["input_file"] ),
                Input(value="output.gif", definition=convert_to_gif.op.inputs["output_file"] ),
                ]
        }
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(test_inputs):
                    print(f"Results : {results}")