from dffml.df.types import Definition
from dffml.df.base import op
from dffml.df.types import DataFlow, Input
from typing import Dict, Any, Union, List
from dffml.base import config


def make_value(val_string: str) -> Union[str, List[str]]:
    if val_string.startswith("[") and val_string.endswith("]"):
        val_string = val_string[1:-1].split(",")

    return val_string


@config
class RunDataFlowConfig:
    dataflow: DataFlow


@op(
    name="dffml.dataflow.run",
    inputs={
        "inputs": Definition(name="flow_inputs", primitive="Dict[str,Any]")
    },
    outputs={
        "results": Definition(name="flow_results", primitive="Dict[str,Any]")
    },
    config_cls=RunDataFlowConfig,
    expand=["results"],
)
async def run_dataflow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
    inputs_created = {}
    definitions = self.config.dataflow.definitions

    for ctx_str, val_defs in inputs.items():
        inputs_created[ctx_str] = [
            Input(
                value=make_value(val_def["value"]),
                definition=definitions[val_def["definition"]],
            )
            for val_def in val_defs
        ]

    async with self.octx.parent(self.config.dataflow) as octx:
        results = [
            {ctx_str: result}
            async for ctx_str, result in octx.run(inputs_created)
        ]

    return {"results": results}
