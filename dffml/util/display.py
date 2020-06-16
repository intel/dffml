"""
Arranges dictionary items in a tabular format.
"""


def create_row(column1, column2, width):
    row = ""
    divider = "+" + "-" * (width) + "+"
    if isinstance(column2, dict):
        row += "|" + column1.center(width) + "|" + "\n" + divider + "\n"
        column1 = "Value:  " + str(column2["value"])
        column2 = "Confidence:   " + str(column2["confidence"])

    row += "|" + column1.center(int(width / 4)) + "|"

    if isinstance(column2, (list, tuple,)):
        row += (
            ", ".join(str(val) for val in column2[: int(width / 10)])
            + f",... (length:{len(column2)})"
        ).center(int(3 * width / 4)) + "|"

    elif isinstance(column2, (str, int, float, bool,)):
        row += str(column2).center(int(3 * width / 4)) + "|"

    else:
        row += "".center(int(3 * width / 4)) + "|"

    row += "\n" + divider
    return row
