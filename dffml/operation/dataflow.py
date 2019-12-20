from typing import Dict, Any, Union, List

from dffml.base import config
from dffml.df.base import op
from dffml.df.types import DataFlow, Input, Definition


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
                value=val_def["value"],
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
