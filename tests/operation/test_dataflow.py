import copy

from dffml.df.types import DataFlow, Input
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.dataflow import run_dataflow, RunDataFlowConfig
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from ..test_df import DATAFLOW, add, mult, parse_line


class TestRunDataFlowOnRecord(AsyncTestCase):
    async def test_run(self):
        test_dataflow = DataFlow(
            operations={
                "run_dataflow": run_dataflow.op,
                "get_single": GetSingle.imp.op,
            },
            configs={"run_dataflow": RunDataFlowConfig(dataflow=DATAFLOW)},
            seed=[
                Input(
                    value=[run_dataflow.op.outputs["results"].name],
                    definition=GetSingle.op.inputs["spec"],
                )
            ],
        )

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
            {
                "mult_op": [
                    {
                        "value": "multiply 42 and 10",
                        "definition": parse_line.op.inputs["line"].name,
                    },
                    {
                        "value": [mult.op.outputs["product"].name],
                        "definition": GetSingle.op.inputs["spec"].name,
                    },
                ]
            },
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
                    self.assertIn("flow_results", results)

                    results = results["flow_results"]
                    self.assertIn(ctx_str, map(str, results.keys()))
                    self.assertIn(ctx_str, test_outputs)

                    results = results[list(results.keys())[0]]
                    self.assertIn("result", results)

                    results = results["result"]
                    expected_results = test_outputs[ctx_str]
                    self.assertEqual(expected_results, results)

    async def test_run_custom(self):
        output_definition = add.op.outputs["sum"]

        get_single_spec_input = Input(
            value=[output_definition.name],
            definition=GetSingle.op.inputs["spec"],
        )

        subflow = copy.deepcopy(DATAFLOW)
        subflow.seed.append(get_single_spec_input)

        test_dataflow = DataFlow(
            operations={
                "run_dataflow": run_dataflow.op._replace(
                    inputs=parse_line.op.inputs,
                    outputs={output_definition.name: output_definition},
                ),
                "get_single": GetSingle.imp.op,
            },
            configs={"run_dataflow": RunDataFlowConfig(dataflow=subflow)},
            seed=[get_single_spec_input],
        )

        test_outputs = {"add 40 and 2": 42, "multiply 42 and 10": 420}

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(test_dataflow) as octx:
                async for _ctx, results in octx.run(
                    {
                        input_line: [
                            Input(
                                value=input_line,
                                definition=parse_line.op.inputs["line"],
                            )
                        ]
                        for input_line in test_outputs
                    }
                ):
                    ctx_str = (await _ctx.handle()).as_string()
                    results = results[output_definition.name]
                    expected_results = test_outputs[ctx_str]
                    self.assertEqual(expected_results, results)
