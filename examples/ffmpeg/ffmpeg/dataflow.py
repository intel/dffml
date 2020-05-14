from dffml import DataFlow, Input, GetSingle
from .operations import convert_to_gif

DATAFLOW = DataFlow.auto(convert_to_gif, GetSingle)
DATAFLOW.seed = [
    Input(
        value=[convert_to_gif.op.outputs["output_file"].name],
        definition=GetSingle.op.inputs["spec"],
    ),
    Input(value=480, definition=convert_to_gif.op.inputs["resolution"]),
]
