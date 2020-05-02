import os
import sys
import pathlib

from dffml.df.types import Input, DataFlow
from dffml.df.base import opimp_in
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from ffmpeg.operations import convert_to_gif


class TestOperations(AsyncTestCase):
    async def setUp(self):
        self.parent_path = pathlib.Path(__file__).parent

    async def tearDown(self):
        os.remove((self.parent_path / "output.gif").as_posix())

    async def test_run(self):
        dataflow = DataFlow.auto(convert_to_gif)
        dataflow.seed.append(
            Input(
                value=1920, definition=convert_to_gif.op.inputs["resolution"]
            )
        )

        input_file_path = self.parent_path / "input.mp4"
        output_file_path = self.parent_path / "output.gif"

        test_inputs = {
            "Test": [
                Input(
                    value=input_file_path.as_posix(),
                    definition=convert_to_gif.op.inputs["input_file"],
                ),
                Input(
                    value=output_file_path.as_posix(),
                    definition=convert_to_gif.op.inputs["output_file"],
                ),
            ]
        }
        self.assertFalse(output_file_path.exists())
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(test_inputs):
                    self.assertTrue(output_file_path.exists())
                    filesize = output_file_path.stat().st_size / (
                        1024 * 1024
                    )  # filesize in MB
                    self.assertGreater(filesize, 2)
