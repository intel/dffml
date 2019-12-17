from dffml.df.types import Definition
from dffml.df.base import op
from dffml.df.types import DataFlow, Input
from typing import Dict, Any, NamedTuple


class RunDataFlowOnRepoConfig(NamedTuple):
    dataflow: DataFlow

    @classmethod
    def _fromdict(cls, **kwargs):
        return cls(**kwargs)


@op(
    inputs={"ins": Definition(name="flow_ins", primitive="Dict[str,Any]")},
    outputs={
        "results": Definition(name="flow_results", primitive="Dict[str,Any]")
    },
    config_cls=RunDataFlowOnRepoConfig,
    expand=["results"],
)
async def run_dataflow_on_repo(self, ins: Dict[str, Any]) -> Dict[str, Any]:
    ins_created = {}
    definitions = self.config.dataflow.definitions
    for ctx_str, val_defs in ins.items():
        ins_created[ctx_str] = [
            Input(
                value=val_def["value"],
                definition=definitions[val_def["definition"]],
            )
            for val_def in val_defs
        ]
    async with self.octx.parent(self.config.dataflow) as octx:
        results = [
            {ctx_str: result}
            async for ctx_str, result in octx.run(ins_created)
        ]

    return {"results": results}
