import copy
import collections
from typing import Dict, Any, NamedTuple, List

from ..df.types import Definition, Stage, DataFlow
from ..df.base import (
    op,
    OperationImplementationContext,
    BaseInputSetContext,
    BaseInputNetworkContext,
)
from ..df.exceptions import DefinitionNotInContext
from ..util.data import traverse_get


class GroupBySpec(NamedTuple):
    group: Definition
    by: Definition

    @classmethod
    async def resolve(
        cls,
        ctx: BaseInputSetContext,
        ictx: BaseInputNetworkContext,
        exported: Dict[str, Any],
    ):
        # TODO Address the need to copy operation implementation inputs dict
        # In case the input is used elsewhere in the network
        exported = copy.deepcopy(exported)
        # Look up the definiton for the group and by fields
        for convert in ["group", "by"]:
            exported[convert] = await ictx.definition(ctx, exported[convert])
        return cls(**exported)


group_by_spec = Definition(name="group_by_spec", primitive="Dict[str, Any]")

group_by_output = Definition(
    name="group_by_output", primitive="Dict[str, List[Any]]"
)


@op(
    name="group_by",
    inputs={"spec": group_by_spec},
    outputs={"output": group_by_output},
    stage=Stage.OUTPUT,
)
class GroupBy(OperationImplementationContext):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Convert group_by_spec into a dict with values being of the NamedTuple
        # type GroupBySpec
        outputs = {
            key: await GroupBySpec.resolve(self.ctx, self.octx.ictx, value)
            for key, value in inputs["spec"].items()
        }
        self.logger.debug("output spec: %s", outputs)
        # Acquire all definitions within the context
        async with self.octx.ictx.definitions(self.ctx) as od:
            # Output dict
            want = {}
            # Group each requested output
            for output_name, output in outputs.items():
                # Create an array for this output data
                want[output_name] = []
                # Create an ordered dict which will be keyed off of and ordered
                # by the values of the output.group definition as seen in the
                # input network context
                group_by = {}
                async for item in od.inputs(output.by):
                    group_by[item.value] = (item, {})
                group_by = collections.OrderedDict(sorted(group_by.items()))
                # Find all inputs within the input network for the by definition
                async for item in od.inputs(output.group):
                    # Get all the parents of the input
                    parents = list(item.get_parents())
                    for group, related in group_by.values():
                        # Ensure that the definition we need to group by is in
                        # the parents
                        if not group in parents:
                            continue
                        if not output.by.name in related:
                            related[output.by.name] = []
                        related[output.by.name].append(item.value)

                for index, (_group, qdata) in group_by.items():
                    for def_name, results in qdata.items():
                        for value in results:
                            want[output_name].insert(index, value)

                # # If only one and single is set then convert list to single
                # # item for output dict
                # if len(want[output_name]) == 1 and output.single:
                #     want[output_name] = want[output_name][0]
                # # If the output needs to be a dict then make it one. This
                # # will convert an array of arrays to a dict.
                # elif output.ismap:
                #     want[output_name] = dict(want[output_name])

            return want


get_multi_spec = Definition(name="get_multi_spec", primitive="array")

get_multi_output = Definition(name="get_multi_output", primitive="map")


@op(
    name="get_multi",
    inputs={"spec": get_multi_spec},
    outputs={"output": get_multi_output},
    stage=Stage.OUTPUT,
)
class GetMulti(OperationImplementationContext):
    """
    Output operation to get all Inputs matching given definitions.

    Parameters
    ----------
    spec : list
        List of definition names. Any Inputs with matching definition will be
        returned.

    Returns
    -------
    dict
        Maps definition names to all the Inputs of that definition

    Examples
    --------

    The following shows how to grab all Inputs with the URL definition. If we
    had we run an operation which output a URL, that output URL would have also
    been returned to us.

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> URL = Definition(name="URL", primitive="string")
    >>>
    >>> dataflow = DataFlow.auto(GetMulti)
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[URL.name],
    ...         definition=GetMulti.op.inputs["spec"]
    ...     )
    ... )
    >>>
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(dataflow, [
    ...         Input(
    ...             value="https://github.com/intel/dffml",
    ...             definition=URL
    ...         ),
    ...         Input(
    ...             value="https://github.com/intel/cve-bin-tool",
    ...             definition=URL
    ...         )
    ...     ]):
    ...         print(results)
    ...
    >>> asyncio.run(main())
    {'URL': ['https://github.com/intel/dffml', 'https://github.com/intel/cve-bin-tool']}
    """

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # TODO Address the need to copy operation implementation inputs dict
        # In case the input is used elsewhere in the network
        exported = copy.deepcopy(inputs["spec"])
        name_map = {}
        for i, input_value in enumerate(exported):
            if isinstance(input_value, dict):
                name, value = list(input_value.items())[0]
                name_map[value] = name
                exported[i] = value

        # Look up the definiton for each
        for convert in range(0, len(exported)):
            exported[convert] = await self.octx.ictx.definition(
                self.ctx, exported[convert]
            )
        self.logger.debug("output spec: %s", exported)
        # Acquire all definitions within the context
        async with self.octx.ictx.definitions(self.ctx) as od:
            # Output dict
            want = {}
            # Group each requested output
            for definition in exported:
                async for item in od.inputs(definition):
                    want.setdefault(definition.name, [])
                    want[definition.name].append(item.value)

            # Rename outputs if present in name_map
            for key, value in want.copy().items():
                if name_map.get(key, None):
                    want[name_map[key]] = value
                    want.pop(key)
            return want


get_single_spec = Definition(name="get_single_spec", primitive="array")

get_single_output = Definition(name="get_single_output", primitive="map")


@op(
    name="get_single",
    inputs={"spec": get_single_spec},
    outputs={"output": get_single_output},
    stage=Stage.OUTPUT,
)
class GetSingle(GetMulti):
    """
    Output operation to get a single Input for each definition given.

    Parameters
    ----------
    spec : list
        List of definition names. An Input with matching definition will be
        returned.

    Returns
    -------
    dict
        Maps definition names to an Input of that definition

    Examples
    --------

    The following shows how to grab an Inputs with the URL definition. If we
    had we run an operation which output a URL, that output URL could have also
    been returned to us.

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> URL = Definition(name="URL", primitive="string")
    >>> ORG = Definition(name="ORG", primitive="string")
    >>>
    >>> dataflow = DataFlow.auto(GetSingle)
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[{"Repo Link": URL.name}, ORG.name],
    ...         definition=GetSingle.op.inputs["spec"]
    ...     )
    ... )
    >>>
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(dataflow, [
    ...         Input(
    ...             value="https://github.com/intel/dffml",
    ...             definition=URL
    ...         ),
    ...         Input(
    ...             value="Intel",
    ...             definition=ORG
    ...         )
    ...     ]):
    ...         print(results)
    ...
    >>> asyncio.run(main())
    {'ORG': 'Intel', 'Repo Link': 'https://github.com/intel/dffml'}
    """

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Output dict
        want = await super().run(inputs)
        for key, value in want.items():
            want[key] = value.pop()
        return want


associate_spec = Definition(name="associate_spec", primitive="List[str]")

associate_output = Definition(
    name="associate_output", primitive="Dict[str, Any]"
)


@op(
    name="associate",
    inputs={"spec": associate_spec},
    outputs={"output": associate_output},
    stage=Stage.OUTPUT,
)
class Associate(OperationImplementationContext):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # TODO Address the need to copy operation implementation inputs dict
        # In case the input is used elsewhere in the network
        exported = copy.deepcopy(inputs["spec"])
        # Look up the definiton for each
        try:
            for convert in range(0, len(exported)):
                exported[convert] = await self.octx.ictx.definition(
                    self.ctx, exported[convert]
                )
        except DefinitionNotInContext:
            return {exported[1]: {}}
        # Make exported into key, value which it will be in output
        key, value = exported
        # Acquire all definitions within the context
        async with self.octx.ictx.definitions(self.ctx) as od:
            # Output dict
            want = {}
            async for item in od.inputs(value):
                parents = item.get_parents()
                for parent in parents:
                    if key == parent.definition:
                        want[parent.value] = item.value
                        break
            return {value.name: want}


@op(
    name="associate_definition",
    inputs={"spec": associate_spec},
    outputs={"output": associate_output},
    stage=Stage.OUTPUT,
)
class AssociateDefinition(OperationImplementationContext):
    """
    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> feed_def = Definition(name="feed", primitive="string")
    >>> dead_def = Definition(name="dead", primitive="string")
    >>> output = Definition(name="output", primitive="string")
    >>>
    >>> feed_input = Input(value="my favorite value", definition=feed_def)
    >>> face_input = Input(
    ...     value="face", definition=output, parents=[feed_input]
    ... )
    >>>
    >>> dead_input = Input(
    ...     value="my second favorite value", definition=dead_def
    ... )
    >>> beef_input = Input(
    ...     value="beef", definition=output, parents=[dead_input]
    ... )
    >>>
    >>> async def main():
    ...     for value in ["feed", "dead"]:
    ...         async for ctx, results in MemoryOrchestrator.run(
    ...             DataFlow.auto(AssociateDefinition),
    ...             [
    ...                 feed_input,
    ...                 face_input,
    ...                 dead_input,
    ...                 beef_input,
    ...                 Input(
    ...                     value={value: "output"},
    ...                     definition=AssociateDefinition.op.inputs["spec"],
    ...                 ),
    ...             ],
    ...         ):
    ...             print(results)
    >>>
    >>> asyncio.run(main())
    {'feed': 'face'}
    {'dead': 'beef'}
    """

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Look up the definiton for each definition name given
        try:
            spec = {
                await self.octx.ictx.definition(
                    self.ctx, key
                ): await self.octx.ictx.definition(self.ctx, value)
                for key, value in inputs["spec"].items()
            }
        except DefinitionNotInContext:
            return {key: {} for key in inputs["spec"]}
        # Output dict
        want = {}
        # Acquire all definitions within the context
        async with self.octx.ictx.definitions(self.ctx) as od:
            # Make exported into key, value which it will be in output
            for key, value in spec.items():
                async for item in od.inputs(value):
                    parents = item.get_parents()
                    for parent in parents:
                        if key.name == parent.definition.name:
                            want[key.name] = item.value
                            break
        return want


class RemapConfig(NamedTuple):
    dataflow: DataFlow

    @classmethod
    def _fromdict(cls, **kwargs):
        kwargs["dataflow"] = DataFlow._fromdict(**kwargs["dataflow"])
        return cls(**kwargs)


class RemapFailure(Exception):
    """
    Raised whem results of a dataflow could not be remapped.
    """


# TODO Make it so that only one output operation gets run, the result of that
# operation is the result of the dataflow
@op(
    inputs={"spec": Definition(name="remap_spec", primitive="map")},
    outputs={"response": Definition(name="remap_output", primitive="map")},
    stage=Stage.OUTPUT,
    config_cls=RemapConfig,
)
async def remap(
    self: OperationImplementationContext, spec: Dict[str, List[str]]
):
    # Create a new orchestrator context. Specify that it should use the existing
    # input set context, this way the output operations we'll be running have
    # access to the data from this data flow rather than a new sub flow.
    async with self.octx.parent(
        self.config.dataflow, reuse={"ictx": self.octx.ictx}
    ) as octx:
        _ctx, result = [result async for result in octx.run(ctx=self.ctx)][0]
    # Remap the output operations to their feature (copied logic
    # from CLI)
    remap = {}
    for (feature_name, traverse) in spec.items():
        try:
            remap[feature_name] = traverse_get(result, *traverse)
        except KeyError as error:
            raise RemapFailure(
                "failed to remap %r. Results do not contain %r: %s"
                % (feature_name, ".".join(traverse), result)
            ) from error
    # Results have been remapped
    return remap
