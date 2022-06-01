from typing import NewType

try:
    import importlib.metadata as importlib_metadata
except:
    import importlib_metadata

import dffml

# TODO Unify make Definitions really Inputs with parents for lineage based of
# Python's typing.
#
# References:
# - https://docs.python.org/3/library/typing.html#newtype
# - https://docs.python.org/3/library/typing.html#user-defined-generic-types
#   - Maybe usful for operations / data structure shorthand for dataflow
#     definition.

SemanticVersion = NewType("SemanticVersion", str)
EntityVersion = NewType("EntityVersion", SemanticVersion)
AliceVersion = NewType("AliceVersion", EntityVersion)

Name = NewType("Name", str)
EntityName = NewType("EntityName", Name)
AliceName = NewType("AliceName", EntityName)


@dffml.op
def alice_version() -> AliceVersion:
    return importlib_metadata.version(__package__)


@dffml.op
def alice_name() -> AliceName:
    return "Alice"


Alice = dffml.SystemContext(
    upstream=dffml.DataFlow(
        operations={"version": alice_version, "name": alice_name}
    ),
)
