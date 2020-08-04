from typing import Dict, Any

from ..base import config
from ..df.base import op, OperationImplementationContext
from ..df.types import DataFlow, Input, Definition


class InvalidCustomRunDataFlowContext(Exception):
    """
    Thrown when custom inputs for dffml.dataflow.run do not list an input with
    string as its primitive as the first input.
    """


class InvalidCustomRunDataFlowOutputs(Exception):
    """
    Thrown when outputs for a custom dffml.dataflow.run do not match that of
    it's subflow.
    """


@config
class RunDataFlowConfig:
    dataflow: DataFlow


DEFAULT_INPUTS = {
    "inputs": Definition(name="flow_inputs", primitive="Dict[str,Any]")
}


@op(
    name="dffml.dataflow.run",
    inputs=DEFAULT_INPUTS,
    outputs={
        "results": Definition(name="flow_results", primitive="Dict[str,Any]")
    },
    config_cls=RunDataFlowConfig,
    expand=["results"],
)
class run_dataflow(OperationImplementationContext):
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

    The following shows how to use run dataflow in its default behavior.

    >>> import asyncio
    >>> from dffml import *
    >>>
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
    >>> dataflow.configs[run_dataflow.op.name] = RunDataFlowConfig(subflow)
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[run_dataflow.op.outputs["results"].name],
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
    ...                 definition=run_dataflow.op.inputs["inputs"]
    ...             )
    ...         ]
    ...     }):
    ...         print(results)
    >>>
    >>> asyncio.run(main())
    {'flow_results': {'dffml': {'URL': 'https://github.com/intel/dffml'}}}

    The following shows how to use run dataflow with custom inputs and outputs.
    This allows you to run a subflow as if it were an operation.

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> URL = Definition(name="URL", primitive="string")
    >>>
    >>> @op(
    ...     inputs={"url": URL},
    ...     outputs={"last": Definition("last_element_in_path", primitive="string")},
    ... )
    ... def last_path(url):
    ...     return {"last": url.split("/")[-1]}
    >>>
    >>> subflow = DataFlow.auto(last_path, GetSingle)
    >>> subflow.seed.append(
    ...     Input(
    ...         value=[last_path.op.outputs["last"].name],
    ...         definition=GetSingle.op.inputs["spec"],
    ...     )
    ... )
    >>>
    >>> dataflow = DataFlow.auto(run_dataflow, GetSingle)
    >>> dataflow.operations[run_dataflow.op.name] = run_dataflow.op._replace(
    ...     inputs={"URL": URL},
    ...     outputs={last_path.op.outputs["last"].name: last_path.op.outputs["last"]},
    ...     expand=[],
    ... )
    >>> dataflow.configs[run_dataflow.op.name] = RunDataFlowConfig(subflow)
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[last_path.op.outputs["last"].name],
    ...         definition=GetSingle.op.inputs["spec"],
    ...     )
    ... )
    >>> dataflow.update(auto_flow=True)
    >>>
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(
    ...         dataflow,
    ...         {
    ...             "run_subflow": [
    ...                 Input(value="https://github.com/intel/dffml", definition=URL)
    ...             ]
    ...         },
    ...     ):
    ...         print(results)
    >>>
    >>> asyncio.run(main())
    {'last_element_in_path': 'dffml'}
    """

    async def run_default(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        The default implementation for the dataflow.run operation is the uctx
        mode. This mode is when we map unique strings to a list of inputs to be
        given to the respective string's context.
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

    async def run_custom(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # TODO Move string primitive validation into init of
        # an OperationImplementation (and then keep this as the context).
        ctx_input_name, ctx_definition = list(self.parent.op.inputs.items())[0]

        if ctx_definition.primitive != "string":
            raise InvalidCustomRunDataFlowContext(ctx_definition.export())

        subflow_inputs = {inputs[ctx_input_name]: []}

        for input_name, value in inputs.items():
            definition = self.parent.op.inputs[input_name]
            subflow_inputs[inputs[ctx_input_name]].append(
                Input(value=value, definition=definition)
            )

        op_outputs = sorted(self.parent.op.outputs.keys())

        async with self.subflow(self.config.dataflow) as octx:
            async for ctx, result in octx.run(subflow_inputs):
                if op_outputs != sorted(result.keys()):
                    raise InvalidCustomRunDataFlowOutputs(
                        ctx_definition.export()
                    )
                return result

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Support redefinition of operation
        if self.parent.op.inputs == DEFAULT_INPUTS:
            return await self.run_default(inputs["inputs"])
        else:
            return await self.run_custom(inputs)
