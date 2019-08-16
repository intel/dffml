import sys

from dffml.df.base import Definition

definitions = [
    Definition(name="UnhashedPassword", primitive="string"),
    Definition(name="ScryptPassword", primitive="string"),
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
