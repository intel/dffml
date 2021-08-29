import sys
from dffml.df.types import Definition

definitions = [
    Definition(name="input_data", primitive="List[List[int]]"),
    Definition(name="output_data", primitive="List[List[int]]"),
    Definition(name="n_components", primitive="int"),
    Definition(name="n_iter", primitive="int"),
    Definition(name="random_state", primitive="int"),
    Definition(name="missing_values", primitive="Any"),
    Definition(name="strategy", primitive="str"),
    Definition(name="categories", primitive="List[List[Any]]"),
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
