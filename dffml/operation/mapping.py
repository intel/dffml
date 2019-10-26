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
    return {"value": traverse_get(mapping, *traverse)}


@op(
    name="dffml.mapping.create",
    inputs={"key": MAPPING_KEY, "value": MAPPING_VALUE},
    outputs={"mapping": MAPPING},
)
def create_mapping(key: str, value: Any):
    return {"mapping": {key: value}}
