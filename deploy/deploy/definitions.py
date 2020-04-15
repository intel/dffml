import sys
from dffml.df.types import Definition

definitions = [
    Definition(name="git_payload_string", primitive="str"),
    Definition(name="git_payload", primitive="Dict[Any]"),
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
