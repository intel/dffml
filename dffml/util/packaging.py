import os
import sys
import venv
import pathlib
import tempfile
import contextlib
from typing import Union


def is_develop(package_name: str) -> Union[bool, pathlib.Path]:
    """
    Returns True if the package is installed in development mode.
    """
    alt_package_name = package_name.replace("-", "_")
    for syspath in map(pathlib.Path, sys.path):
        # Check if egg-link is present
        egg_link = syspath / f"{package_name}.egg-link"
        alt_egg_link = syspath / f"{alt_package_name}.egg-link"
        if egg_link.is_file():
            return pathlib.Path(egg_link.read_text().split("\n")[0])
        elif alt_egg_link.is_file():
            return pathlib.Path(alt_egg_link.read_text().split("\n")[0])
        # Check if path entry is parent of module directory itself
        module_dir = syspath / f"{alt_package_name}"
        if module_dir.is_dir():
            return syspath
    return False


@contextlib.contextmanager
def mkvenv():
    """
    Create a new virtual environment in a temporary directory, and set the
    ``VIRTUAL_ENV`` environment variable appropriately. The newly created
    temporary directory which will be the parent of the new virtual environment,
    which will be in the ``.venv`` directory.

    Examples
    --------

    >>> import sys
    >>> import subprocess
    >>> from dffml import chdir, mkvenv
    >>>
    >>> with mkvenv() as tempdir:
    ...     with chdir(tempdir):
    ...         subprocess.check_call([
    ...             sys.executable,
    ...             "-m",
    ...             "pip",
    ...             "install",
    ...             "pip",
    ...         ])
    0
    """
    with tempfile.TemporaryDirectory() as tempdir:
        # Create virtualenv
        venv_dir = os.path.join(tempdir, ".venv")
        venv.create(venv_dir, with_pip=True)
        # Set VIRTUAL_ENV environment variable
        old_venv = os.getenv("VIRTUAL_ENV", None)
        os.environ["VIRTUAL_ENV"] = venv_dir
        yield tempdir
        # Remove and or reset VIRTUAL_ENV environment variable
        del os.environ["VIRTUAL_ENV"]
        if old_venv:
            os.environ["VIRTUAL_ENV"] = old_venv
