import os
import sys
import pathlib
import tempfile

from dffml import (
    op,
    Input,
    DataFlow,
    GetSingle,
    MemoryOrchestrator,
    AsyncTestCase,
)

from .operations import convert_to_gif


class TestOperations(AsyncTestCase):
    async def setUp(self):
        self.parent_path = pathlib.Path(__file__).parent

    async def test_run(self):
        op()(convert_to_gif)
        dataflow = DataFlow.auto(convert_to_gif, GetSingle)
        dataflow.seed.append(
            Input(
                value=[convert_to_gif.op.outputs["result"].name],
                definition=GetSingle.op.inputs["spec"],
            )
        )
        dataflow.implementations[convert_to_gif.op.name] = convert_to_gif.imp

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
                    idx = "examples.ffmpeg.operations:convert_to_gif.outputs.result"
                    self.assertIn(
                        idx, results,
                    )
                    results = results[idx]
                    self.assertIn("output_file", results)
                    output = results["output_file"]
                    self.assertGreater(len(output), 100000)
