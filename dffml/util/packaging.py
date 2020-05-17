import sys
import pathlib
from typing import Union


def is_develop(package_name: str) -> Union[bool, pathlib.Path]:
    """
    Returns True if the package is installed in development mode.
    """
    for syspath in map(pathlib.Path, sys.path):
        # Check if egg-link is present
        egg_link = syspath / f"{package_name}.egg-link"
        if egg_link.is_file():
            return pathlib.Path(egg_link.read_text().split("\n")[0])
        # Check if path entry is parent of module directory itself
        module_dir = syspath / f"{package_name.replace('-', '_')}"
        if module_dir.is_dir():
            return syspath
    return False
