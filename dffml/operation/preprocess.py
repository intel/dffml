import ast
from dffml.df.types import Definition
from dffml.df.base import op


# Definitions
InputStr = Definition(name="InputStr", primitive="str")
EvaluatedStr = Definition(name="EvaluatedStr", primitive="generic")


@op(
    inputs={"InputStr": InputStr},
    outputs={"EvaluatedStr": EvaluatedStr},
    conditions=[],
)
async def literal_eval(InputStr: str):
    value = ast.literal_eval(InputStr)
    return {"EvaluatedStr": value}
