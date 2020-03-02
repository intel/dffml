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
    Starts a subflow ``self.config.dataflow`` and adds ``inputs`` in it.

    Parameters
    ----------
    inputs : dict
        The inputs to add to the subflow. These should be a key value mapping of
        the context string to the inputs which should be seeded for that context
        string.

    Returns
    -------
    dict
        Maps context strings in inputs to output after running through dataflow.

    Examples
    --------

    >>> URL = Definition(name="URL", primitive="string")
    >>>
    >>> subflow = DataFlow.auto(GetSingle)
    >>> subflow.definitions[URL.name] = URL
    >>> subflow.seed.append(
    ...     Input(
    ...         value=[URL.name],
    ...         definition=GetSingle.op.inputs["spec"]
    ...     )
    ... )
    >>>
    >>> dataflow = DataFlow.auto(run_dataflow, GetSingle)
    >>> dataflow.configs[run_dataflow.imp.op.name] = RunDataFlowConfig(subflow)
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[run_dataflow.imp.op.outputs["results"].name],
    ...         definition=GetSingle.op.inputs["spec"]
    ...     )
    ... )
    >>>
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(dataflow, {
    ...         "run_subflow": [
    ...             Input(
    ...                 value={
    ...                     "dffml": [
    ...                         {
    ...                             "value": "https://github.com/intel/dffml",
    ...                             "definition": URL.name
    ...                         }
    ...                     ]
    ...                 },
    ...                 definition=run_dataflow.imp.op.inputs["inputs"]
    ...             )
    ...         ]
    ...     }):
    ...         print(results)
    >>>
    >>> asyncio.run(main())
    {'flow_results': {'dffml': {'URL': 'https://github.com/intel/dffml'}}}
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
    async with self.subflow(self.config.dataflow) as octx:
        results = [
            {(await ctx.handle()).as_string(): result}
            async for ctx, result in octx.run(inputs_created)
        ]

    return {"results": results}
