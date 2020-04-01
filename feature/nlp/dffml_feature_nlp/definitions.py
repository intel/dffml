import sys
from dffml.df.types import Definition

definitions = [
    Definition(name="UserInput", primitive="str"),
    Definition(name="DataToPrint", primitive="str"),
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
