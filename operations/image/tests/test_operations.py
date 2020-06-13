import numpy as np

from dffml.df.types import Input, DataFlow
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operations_image.operations import resize

dataflow = DataFlow.auto(resize, GetSingle)
dataflow.seed.append(
    Input(
        value=[resize.op.outputs["result"].name,],
        definition=GetSingle.op.inputs["spec"],
    )
)


class TestOperations(AsyncTestCase):
    async def test_resize(self):
        input_array = np.zeros((100, 100, 3), dtype=np.uint8)
        output_array = np.zeros((50 * 50), dtype=np.uint8)
        async for ctx, results in MemoryOrchestrator.run(
            dataflow,
            [
                Input(value=input_array, definition=resize.op.inputs["data"],),
                Input(
                    value=[100, 100, 3],
                    definition=resize.op.inputs["old_dim"],
                ),
                Input(value=[50, 50], definition=resize.op.inputs["new_dim"],),
            ],
        ):
            self.assertEqual(
                results[resize.op.outputs["result"].name].tolist(),
                output_array.tolist(),
            )
