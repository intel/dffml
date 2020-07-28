from typing import Dict, List, Any

from ..df.types import Definition
from ..df.base import op
from ..util.data import traverse_get

MAPPING = Definition(name="mapping", primitive="map")
MAPPING_TRAVERSE = Definition(name="mapping_traverse", primitive="List[str]")
MAPPING_KEY = Definition(name="key", primitive="str")
MAPPING_VALUE = Definition(name="value", primitive="generic")


@op(
    name="dffml.mapping.extract",
    inputs={"mapping": MAPPING, "traverse": MAPPING_TRAVERSE},
    outputs={"value": MAPPING_VALUE},
)
def mapping_extract_value(mapping: Dict[str, Any], traverse: List[str]):
    """
    Extracts value from a given mapping.

    Parameters
    ----------
    mapping : dict
        The mapping to extract the value from.
    traverse : list[str]
        A list of keys to traverse through the mapping dictionary and extract the values.

    Returns
    -------
    dict
        A dictionary containing the value of the keys.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> dataflow = DataFlow.auto(mapping_extract_value, GetSingle)
    >>>
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[mapping_extract_value.op.outputs["value"].name],
    ...         definition=GetSingle.op.inputs["spec"],
    ...     )
    ... )
    >>> inputs = [
    ...     Input(
    ...         value={"key1": {"key2": 42}},
    ...         definition=mapping_extract_value.op.inputs["mapping"],
    ...     ),
    ...     Input(
    ...         value=["key1", "key2"],
    ...         definition=mapping_extract_value.op.inputs["traverse"],
    ...     ),
    ... ]
    >>>
    >>> async def main():
    ...     async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
    ...         print(result)
    >>>
    >>> asyncio.run(main())
    {'value': 42}
    """
    return {"value": traverse_get(mapping, *traverse)}


@op(
    name="dffml.mapping.create",
    inputs={"key": MAPPING_KEY, "value": MAPPING_VALUE},
    outputs={"mapping": MAPPING},
)
def create_mapping(key: str, value: Any):
    """
    Creates a mapping of a given key and value.

    Parameters
    ----------
    key : str
        The key for the mapping.
    value : Any
        The value for the mapping.

    Returns
    -------
    dict
        A dictionary containing the mapping created.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> dataflow = DataFlow.auto(create_mapping, GetSingle)
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[create_mapping.op.outputs["mapping"].name],
    ...         definition=GetSingle.op.inputs["spec"],
    ...     )
    ... )
    >>> inputs = [
    ...     Input(
    ...         value="key1", definition=create_mapping.op.inputs["key"],
    ...     ),
    ...     Input(
    ...         value=42, definition=create_mapping.op.inputs["value"],
    ...     ),
    ... ]
    >>>
    >>> async def main():
    ...     async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
    ...         print(result)
    >>>
    >>> asyncio.run(main())
    {'mapping': {'key1': 42}}
    """
    return {"mapping": {key: value}}
