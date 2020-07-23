from typing import Any

from ..df.types import Definition, GENERIC
from ..df.base import op
from ..util.data import traverse_get, merge

ARRAY = Definition(name="array", primitive="array")
ARRAY_INDEX = Definition(name="array_index", primitive="integer")


@op(
    name="dffml.array.extract",
    inputs={"array": ARRAY, "index": ARRAY_INDEX},
    outputs={"value": GENERIC},
)
def array_extract_value(array: list, index: int):
    return {"value": array[index]}


@op(
    name="dffml.array.create",
    inputs={"value": GENERIC},
    outputs={"array": ARRAY},
)
def array_create(value: Any):
    return {"array": [value]}


@op(
    name="dffml.array.append",
    inputs={"array": ARRAY, "value": GENERIC},
    outputs={"array": ARRAY},
)
def array_append(array: list, value: Any):
    return {"array": array + [value]}
