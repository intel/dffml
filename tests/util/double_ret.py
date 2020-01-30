from typing import Optional, Dict, Any, Tuple


def double_ret(
    super_cool_arg, *, other_very_cool_arg: Optional[Dict[str, Any]] = None
) -> Tuple[str, Tuple]:
    """
    This is the short description.

    This is the longer description.

    Parameters
    ----------
    super_cool_arg : str
        Argument we want the string value of.
    other_very_cool_arg : dict, optional
        Dictionary we want to turn into a tuple of (keys, values).

    Returns
    -------
    str_super_cool_arg : str
        ``super_cool_arg`` as a string
    keys_and_values : tuple
        Keys and values of ``other_very_cool_arg`` returned as a tuple. Keys
        are at index 0, values are at index 1.

    Examples
    -------
    Here's how you use use this function

    >>> double_ret(42, other_very_cool_arg={"feed": 0xFACE})
    ("42", ("feed"], [0xFACE],))
    """
    if other_very_cool_arg is None:
        other_very_cool_arg = {}
    return (
        str(super_cool_arg),
        tuple(other_very_cool_arg.keys(), other_very_cool_arg.values()),
    )
