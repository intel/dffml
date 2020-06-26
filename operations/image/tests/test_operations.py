import cv2
import numpy as np

from dffml.df.types import Input, DataFlow
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operations_image.operations import (
    resize,
    flatten,
    convert_color,
    calcHist,
    Haralick,
    HuMoments,
    normalize,
)


class TestOperations(AsyncTestCase):
    INPUT_ARRAY = np.random.randint(50, 200, (10, 10, 3), dtype=np.uint8)

    async def test_flatten(self):
        input_array = np.zeros((100, 100, 3), dtype=np.uint8)
        output_array = [0] * (100 * 100 * 3)
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(flatten, GetSingle),
            [
                Input(
                    value=[flatten.op.outputs["result"].name,],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_array, definition=flatten.op.inputs["array"],
                ),
            ],
        ):
            self.assertEqual(
                results[flatten.op.outputs["result"].name].tolist(),
                output_array,
            )

    async def test_resize(self):
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(resize, GetSingle),
            [
                Input(
                    value=[resize.op.outputs["result"].name,],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=self.INPUT_ARRAY, definition=resize.op.inputs["src"],
                ),
                Input(
                    value=[50, 50, 3], definition=resize.op.inputs["dsize"],
                ),
            ],
        ):
            self.assertEqual(
                results[resize.op.outputs["result"].name].shape, (50, 50, 3),
            )

    async def test_convert_color(self):
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(convert_color, GetSingle),
            [
                Input(
                    value=[convert_color.op.outputs["result"].name,],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=self.INPUT_ARRAY,
                    definition=convert_color.op.inputs["src"],
                ),
                Input(
                    value="BGR2RGB",
                    definition=convert_color.op.inputs["code"],
                ),
            ],
        ):
            self.assertEqual(
                cv2.cvtColor(
                    results[convert_color.op.outputs["result"].name],
                    cv2.COLOR_RGB2BGR,
                )
                .flatten()
                .tolist(),
                self.INPUT_ARRAY.flatten().tolist(),
            )

    async def test_calcHist(self):
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(calcHist, GetSingle),
            [
                Input(
                    value=[calcHist.op.outputs["result"].name,],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=self.INPUT_ARRAY,
                    definition=calcHist.op.inputs["images"],
                ),
                Input(value=None, definition=calcHist.op.inputs["mask"],),
                Input(
                    value=[0, 1], definition=calcHist.op.inputs["channels"],
                ),
                Input(
                    value=[32, 32], definition=calcHist.op.inputs["histSize"],
                ),
                Input(
                    value=[0, 256, 0, 256],
                    definition=calcHist.op.inputs["ranges"],
                ),
            ],
        ):
            self.assertEqual(
                results[calcHist.op.outputs["result"].name].shape, (32, 32)
            )

    async def test_Haralick(self):
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(Haralick, GetSingle),
            [
                Input(
                    value=[Haralick.op.outputs["result"].name,],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=self.INPUT_ARRAY, definition=Haralick.op.inputs["f"],
                ),
            ],
        ):
            self.assertEqual(
                results[Haralick.op.outputs["result"].name].shape, (13,)
            )

    async def test_HuMoments(self):
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(HuMoments, GetSingle),
            [
                Input(
                    value=[HuMoments.op.outputs["result"].name,],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=self.INPUT_ARRAY,
                    definition=HuMoments.op.inputs["m"],
                ),
            ],
        ):
            self.assertEqual(
                results[HuMoments.op.outputs["result"].name].shape, (7,)
            )

    async def test_normalize(self):
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(normalize, GetSingle),
            [
                Input(
                    value=[normalize.op.outputs["result"].name,],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=self.INPUT_ARRAY,
                    definition=normalize.op.inputs["src"],
                ),
            ],
        ):
            self.assertEqual(
                results[normalize.op.outputs["result"].name].shape,
                self.INPUT_ARRAY.shape,
            )
