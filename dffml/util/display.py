"""
Arranges dictionary items in a tabular format.
"""


def create_row(column1, column2, width):
    row = ""
    divider = "+" + "-" * (width) + "+"
    column1_width = int(width / 4)
    column2_width = width - column1_width - 1

    if isinstance(column2, dict):
        row += "|" + column1.center(width) + "|" + "\n" + divider + "\n"
        column1 = "Value:  " + str(column2["value"])
        column2 = "Confidence:   " + str(column2["confidence"])

    row += "|" + column1[:column1_width].center(column1_width) + "|"

    if isinstance(column2, (list, tuple,)):
        row += (
            str(column2)[1 : int(width / 3)] + f" ... (length:{len(column2)})"
        ).center(column2_width) + "|"

    elif isinstance(column2, (str, int, float, bool,)):
        row += str(column2).center(column2_width) + "|"

    else:
        row += "".center(column2_width) + "|"

    row += "\n" + divider
    return row
