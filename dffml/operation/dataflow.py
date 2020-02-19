from typing import Dict, Any

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
    """
        params:
            inputs: Dict -> {
                "ctx_str" : [
                    {
                        "value":val1,
                        "defintion":defintion1
                    },
                    {
                        "value":val2,
                        "defintion":defintion2
                    }
                ]
            }
    """
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
        # Register the subflow with parent,so that parent flow can
        # forward inputs of specifed defintions(in DataFlow.forward)
        print(f"Registering subflow")
        await self.octx.register_subflow(self.parent.op.instance_name, octx)
        results = [
            {(await ctx.handle()).as_string(): result}
            async for ctx, result in octx.run(inputs_created)
        ]

    return {"results": results}
