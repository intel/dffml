import sys
from dffml.df.types import Definition

definitions = [
    Definition(name="input_file", primitive="str"),
    Definition(name="output_file", primitive="str"),

]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
