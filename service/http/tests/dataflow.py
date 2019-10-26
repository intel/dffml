import copy
from typing import NamedTuple, Dict, List

from dffml.df.base import op, OperationImplementationContext
from dffml.df.types import Input, Stage, Definition, DataFlow
from dffml.operation.output import GetSingle, remap


class FormatterConfig(NamedTuple):
    formatting: str


@op(
    inputs={"data": Definition(name="format_data", primitive="string")},
    outputs={"string": Definition(name="message", primitive="string")},
    config_cls=FormatterConfig,
)
def formatter(data: str, op_config: FormatterConfig):
    return {"string": op_config.formatting.format(data)}


HELLO_BLANK_DATAFLOW = DataFlow(
    operations={"hello_blank": formatter.op, "remap_to_response": remap.op},
    configs={
        "hello_blank": {"formatting": "Hello {}"},
        "remap_to_response": {
            "dataflow": DataFlow(
                operations={"get_formatted_message": GetSingle.op},
                seed=[
                    Input(
                        value=[formatter.op.outputs["string"].name],
                        definition=GetSingle.op.inputs["spec"],
                    )
                ],
            )
        },
    },
    seed=[
        Input(
            value={"response": [formatter.op.outputs["string"].name]},
            definition=remap.op.inputs["spec"],
        )
    ],
)

HELLO_WORLD_DATAFLOW = copy.deepcopy(HELLO_BLANK_DATAFLOW)
HELLO_WORLD_DATAFLOW.seed.append(
    Input(value="World", definition=formatter.op.inputs["data"])
)
