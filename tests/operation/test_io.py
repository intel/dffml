import io
import builtins
import contextlib
from unittest import mock

from dffml.df.base import op
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase
from dffml.df.types import DataFlow, Input, Definition
from dffml.operation.io import AcceptUserInput, printOutput


class TestInputOutput(AsyncTestCase):
    async def setUp(self):
        super().setUp()
        self.stdout = io.StringIO()
        InputDataflow = DataFlow(
            operations={
                "AcceptUserInput": AcceptUserInput.op,
                "get_single": GetSingle.imp.op,
            },
            seed=[
                Input(
                    value=[AcceptUserInput.op.outputs["InputData"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ],
            implementations={AcceptUserInput.op.name: AcceptUserInput},
        )

        OutputDataflow = DataFlow(
            operations={
                "printOutput": printOutput.op,
                "get_single": GetSingle.imp.op,
            },
            implementations={printOutput.op.name: printOutput.imp},
        )

        self.InputDataflow = InputDataflow
        self.OutputDataflow = OutputDataflow

    async def test_AcceptUserInput(self):
        test_inputs = {"testInput": []}
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(self.InputDataflow) as octx:
                with mock.patch(
                    "builtins.input", return_value="Testing AcceptUserInput"
                ):
                    async for ctx_str, results in octx.run(test_inputs):
                        self.assertIn("UserInput", results)
                        self.assertEqual(
                            "Testing AcceptUserInput",
                            results["UserInput"]["data"],
                        )

    async def test_printOutput(self):
        test_inputs = [
            Input(
                value="Testing printOutput",
                definition=self.OutputDataflow.definitions["DataToPrint"],
                parents=None,
            )
        ]
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(self.OutputDataflow) as octx:
                with contextlib.redirect_stdout(self.stdout):
                    async for ctx_str, _ in octx.run(test_inputs):
                        results = self.stdout.getvalue()
                        self.assertIn("Testing printOutput", results)
