import io
import builtins
import contextlib
from unittest import mock

from dffml.df.base import op
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase
from dffml.df.types import DataFlow, Input, Definition
from dffml.operation.io import AcceptUserInput, print_output


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
                "print_output": print_output.op,
                "get_single": GetSingle.imp.op,
            },
            implementations={print_output.op.name: print_output.imp},
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
                            "Testing AcceptUserInput", results["UserInput"]
                        )

    async def test_print_output(self):
        test_inputs = [
            Input(
                value="Testing print_output",
                definition=self.OutputDataflow.definitions["DataToPrint"],
                parents=None,
            )
        ]
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(self.OutputDataflow) as octx:
                with contextlib.redirect_stdout(self.stdout):
                    async for ctx_str, _ in octx.run(test_inputs):
                        results = self.stdout.getvalue()
                        self.assertIn("Testing print_output", results)
