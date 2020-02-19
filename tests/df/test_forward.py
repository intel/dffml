from dffml.df.types import DataFlow, Definition, Input
from dffml.df.base import op
from dffml.operation.dataflow import run_dataflow, RunDataFlowConfig
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.mapping import MAPPING
from dffml.df.memory import MemoryOrchestrator

INPUT_VECTOR = Definition(name="input_vector", primitive="List[float]")
VECTOR = Definition(name="vector", primitive="List[float]")
MATRIX = Definition(name="matrix", primitive="List[List[float]]")
NORMALIZED_VECTOR = Definition(
    name="normalized_vector", primitive="List[float]"
)
SHAPE = Definition(name="shape", primitive="List[int]")


@op(inputs={"input_vector": INPUT_VECTOR}, outputs={"vector": VECTOR})
def echo_vector(input_vector):
    return {"vector": input_vector}


@op(
    inputs={"input_vector": VECTOR},
    outputs={"output_vector": NORMALIZED_VECTOR},
)
def normalize(input_vector):
    s = sum(input_vector)
    return {"output_vector": [x / s for x in input_vector]}


@op(
    inputs={"input_vector": NORMALIZED_VECTOR, "shape": SHAPE},
    outputs={"matrix": MATRIX},
)
def reshape(input_vector, shape):
    m, n = shape
    matrix = [input_vector[i * n : (i + 1) * n] for i in range(m)]
    return {"matrix": matrix}


@op(
    inputs={"input_vector": VECTOR, "matrix": MATRIX},
    outputs={"data": MAPPING},
)
def collect_data(input_vector, matrix):
    return {"data": {"input_vector": input_vector, "matrix": matrix,}}


# TODO
# CAN ONLY FORWARD OUTPUT OF OPERATIONS NOW FIX THIS
# Run dataflow needs to be the first operation in the list for
# subflow to be registered


class TestRunDataFlowOnRepo(AsyncTestCase):
    async def test_run(self):
        norm_shape_flow = DataFlow(
            operations={
                "normalizer": normalize.op,
                "reshaper": reshape.op,
                "collector": collect_data.op,
                "get_single": GetSingle.imp.op,
            },
            seed=[
                # Input(
                #     value=[VECTOR.name],
                #     definition=GetSingle.op.inputs["spec"],
                # ),
                Input(value=[2, 3], definition=SHAPE),
                Input(
                    value=[collect_data.op.outputs["data"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
            ],
            implementations={
                normalize.op.name: normalize.imp,
                reshape.op.name: reshape.imp,
                collect_data.op.name: collect_data.imp,
            },
        )
        master_flow = DataFlow(
            operations={
                "run_normalizing_flow": run_dataflow.op,
                "get_single": GetSingle.imp.op,
                "echo_vector": echo_vector.op,
            },
            configs={
                "run_normalizing_flow": RunDataFlowConfig(
                    dataflow=norm_shape_flow
                )
            },
            seed=[
                Input(
                    value=[run_dataflow.op.outputs["results"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(value=[1, 2, 3, 1, 2, 3], definition=INPUT_VECTOR),
            ],
            implementations={echo_vector.op.name: echo_vector.imp,},
        )
        master_flow.forward.add("run_normalizing_flow", [VECTOR])

        test_inputs = [
            {
                "feature1": []
                # Input(value=[1, 2, 3, 1, 2, 3], definition=INPUT_VECTOR),
                # Input(value={}, definition=run_dataflow.op.inputs["inputs"]),
            }
        ]
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(master_flow) as octx:
                async for ctx_str, results in octx.run(
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
                    print(f"Debug ctx_str:{ctx_str},results:{results}")
