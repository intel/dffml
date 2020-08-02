import ast

from ..df.types import Definition
from ..df.base import op


# Definitions
InputStr = Definition(name="InputStr", primitive="str")
EvaluatedStr = Definition(name="EvaluatedStr", primitive="generic")


@op(
    inputs={"str_to_eval": InputStr},
    outputs={"str_after_eval": EvaluatedStr},
    conditions=[],
)
async def literal_eval(str_to_eval: str):
    """
    Evaluate the input using ast.literal_eval()

    Parameters
    ----------
    str_to_eval : str
        A string to be evaluated.

    Returns
    -------
    dict
        A dict containing python literal.

    Examples
    --------

    The following example shows how to use literal_eval.

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> dataflow = DataFlow.auto(literal_eval, GetSingle)
    >>> dataflow.seed.append(
    ...    Input(
    ...        value=[literal_eval.op.outputs["str_after_eval"].name,],
    ...        definition=GetSingle.op.inputs["spec"],
    ...    )
    ... )
    >>> inputs = [
    ...    Input(
    ...        value="[1,2,3]",
    ...        definition=literal_eval.op.inputs["str_to_eval"],
    ...        parents=None,
    ...    )
    ... ]
    >>>
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(dataflow, inputs):
    ...         print(results)
    >>>
    >>> asyncio.run(main())
    {'EvaluatedStr': [1, 2, 3]}
    """
    value = ast.literal_eval(str_to_eval)
    return {"str_after_eval": value}
