import sys
from dffml.df.types import Definition

definitions = [
    Definition(name="calc_string", primitive="str"),
    Definition(name="is_add", primitive="bool"),
    Definition(name="is_mult", primitive="bool"),
    Definition(name="numbers", primitive="List[int]"),
    Definition(name="result", primitive="int"),
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
