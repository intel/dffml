import sys
from dffml.df.types import Definition

definitions = [
    Definition(name="Input_file", primitive="bytes"),
    Definition(name="Resolution", primitive="int"),
    Definition(name="Output_file", primitive="bytes"),
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
