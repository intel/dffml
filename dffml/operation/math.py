from ..df.types import Definition
from ..df.base import op

# Definitions
multiplicand_def = Definition(name="multiplicand_def", primitive="generic")
multiplier_def = Definition(name="multiplier_def", primitive="generic")
product_def = Definition(name="product", primitive="generic")


@op(
    name="multiply",
    inputs={"multiplicand": multiplicand_def, "multiplier": multiplier_def},
    outputs={"product": product_def},
)
async def multiply(multiplicand, multiplier):
    """
    Multiply record values

    Parameters
    ----------
    multiplicand : generic
        An arithmetic type value.
    multiplier : generic
        An arithmetic type value.

    Returns
    -------
    dict
        A dict containing the product.

    Examples
    --------

    The following example shows how to use multiply.

    >>> import asyncio
    >>> from dffml import *
    >>> 
    >>> dataflow = DataFlow.auto(multiply, GetSingle)
    >>> dataflow.seed.append(
    ...    Input(
    ...        value=[multiply.op.outputs["product"].name,],
    ...        definition=GetSingle.op.inputs["spec"],
    ...    )
    ... )
    >>> inputs = [
    ...    Input(
    ...        value=12,
    ...        definition=multiply.op.inputs["multiplicand"],
    ...    ),
    ...    Input(
    ...        value=3,
    ...        definition=multiply.op.inputs["multiplier"],
    ...    ),
    ... ]
    >>> 
    >>> async def main():
    ...     async for ctx, results in MemoryOrchestrator.run(dataflow, inputs):
    ...         print(results)
    >>> 
    >>> asyncio.run(main())
    {'product': 36}
    """
    if isinstance(multiplicand, (list, tuple,)):
        value = type(multiplicand)(
            [element * multiplier for element in multiplicand]
        )
    else:
        value = multiplicand * multiplier
    return {"product": value}
