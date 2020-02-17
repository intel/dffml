import io
import json
import unittest.mock

from dffml.df.types import DataFlow, Input, Definition
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.dataflow import run_dataflow, RunDataFlowConfig
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase
from dffml.df.base import op

from ..test_df import DATAFLOW, add, mult, parse_line

STRING_IN = Definition(name="input_string", primitive="str")
STRING_OUT = Definition(name="output_string", primitive="str")


@op(inputs={"input_string": STRING_IN}, outputs={"output_string": STRING_OUT})
def echo(input_string):
    print(f"Debug ECHO was called with {input_string}")
    return {"output_string": input_string}


class TestRunDataFlowOnRepo(AsyncTestCase):
    async def test_run(self):
        DATAFLOW.seed.append(
            Input(
                value=[STRING_OUT.name],
                definition=GetSingle.op.inputs["spec"],
            )
        )
        test_dataflow = DataFlow(
            operations={
                "run_dataflow": run_dataflow.op,
                "get_single": GetSingle.imp.op,
                "echo_operation": echo.op,
            },
            configs={"run_dataflow": RunDataFlowConfig(dataflow=DATAFLOW)},
            seed=[
                Input(
                    value=[run_dataflow.op.outputs["results"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(value="SHOUTOUT", definition=STRING_IN),
            ],
            implementations={echo.op.name: echo.imp},
        )

        test_dataflow.forward.add("run_dataflow", [STRING_OUT])

        test_inputs = [
            {
                "add_op": [
                    {
                        "value": "add 40 and 2",
                        "definition": parse_line.op.inputs["line"].name,
                    },
                    {
                        "value": [add.op.outputs["sum"].name],
                        "definition": GetSingle.op.inputs["spec"].name,
                    },
                ]
            },
            # {
            #     "mult_op": [
            #         {
            #             "value": "multiply 42 and 10",
            #             "definition": parse_line.op.inputs["line"].name,
            #         },
            #         {
            #             "value": [mult.op.outputs["product"].name],
            #             "definition": GetSingle.op.inputs["spec"].name,
            #         },
            #     ]
            # },
        ]
        test_outputs = {"add_op": 42, "mult_op": 420}
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(test_dataflow) as octx:
                async for _ctx, results in octx.run(
                    {
                        list(test_input.keys())[0]: [
                            Input(
                                value=test_input,
                                definition=run_dataflow.op.inputs["inputs"],
                            )
                        ]
                        for test_input in test_inputs
                    }
                ):
                    ctx_str = (await _ctx.handle()).as_string()
                    print(f"DEbug flow_results : {results}")
                    self.assertIn("flow_results", results)

                    results = results["flow_results"]
                    self.assertIn(ctx_str, map(str, results.keys()))
                    self.assertIn(ctx_str, test_outputs)

                    results = results[list(results.keys())[0]]
                    self.assertIn("result", results)

                    results = results["result"]
                    expected_results = test_outputs[ctx_str]
                    self.assertEqual(expected_results, results)
