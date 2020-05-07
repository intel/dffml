import os
import sys
import pathlib
import tempfile


from dffml.df.types import Input, DataFlow
from dffml.df.base import opimp_in
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from ffmpeg.operations import convert_to_gif
from dffml.operation.output import GetSingle


class TestOperations(AsyncTestCase):
    async def setUp(self):
        self.parent_path = pathlib.Path(__file__).parent

    async def test_run(self):
        dataflow = DataFlow.auto(convert_to_gif, GetSingle)
        dataflow.seed.append(
            Input(
                value=[convert_to_gif.op.outputs["output_file"].name],
                definition=GetSingle.op.inputs["spec"],
            )
        )

        input_file_path = self.parent_path / "input.mp4"

        with open(input_file_path, "rb") as f:
            input_file = f.read(-1)

        test_inputs = {
            "Test": [
                Input(
                    value=input_file,
                    definition=convert_to_gif.op.inputs["input_file"],
                ),
                Input(
                    value=240,
                    definition=convert_to_gif.op.inputs["resolution"],
                ),
            ]
        }

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(test_inputs):
                    self.assertIn("Output_file", results)
                    output = results["Output_file"]
                    self.assertGreater(len(output), 100000)
