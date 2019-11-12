import sys
import pathlib
from typing import Union


def is_develop(pacakge_name: str) -> Union[bool, pathlib.Path]:
    """
    Returns True if the package is installed in development mode.
    """
    for syspath in map(pathlib.Path, sys.path):
        egg_link = syspath / f"{pacakge_name}.egg-link"
        if egg_link.is_file():
            return pathlib.Path(egg_link.read_text().split("\n")[0])
    return False
