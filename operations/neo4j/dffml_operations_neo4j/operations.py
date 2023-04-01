from typing import List

from dffml.df.base import op

from .definitions import calc_string, is_add, is_mult, numbers, result


@op(inputs={"numbers": numbers}, outputs={"sum": result}, conditions=[is_add])
async def calc_add(numbers: List[int]):
    """
    Sum of a list of numbers
    """
    return {"sum": sum(numbers)}


@op(
    inputs={"numbers": numbers},
    outputs={"product": result},
    conditions=[is_mult],
)
async def calc_mult(numbers: List[int]):
    """
    Multiply a list of numbers together
    """
    product = 1
    for number in numbers:
        product *= number
    return {"product": product}


@op(
    inputs={"line": calc_string},
    outputs={"add": is_add, "mult": is_mult, "numbers": numbers},
)
async def calc_parse_line(line: str):
    """
    Parse a line which holds the English form of a math calculation to be done
    """
    return {
        "add": "add" in line,
        "mult": "mult" in line,
        "numbers": [int(item) for item in line.split() if item.isdigit()],
    }
