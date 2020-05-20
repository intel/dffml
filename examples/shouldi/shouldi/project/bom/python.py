import pathlib
from typing import List, Optional

from dffml import SetupPyKWArg

from .base import BOM, Dependency
from .db.pypi import PyPiDB


def python_requirements_to_bom(requirements):

    bom = BOM(dependencies=[])
    pypi = PyPiDB("pypi")
    for package in requirements:
        version = None
        if not package.isalnum():
            # From PEP-440
            for split in ["===", "~=", ">=", "<=", "==", "!=", "<", ">"]:
                if split in package:
                    name, version = package.split(split)
                    break
            bom.dependencies.append(
                pypi.lookup(
                    Dependency(
                        uuid=None, name=name, url=None, license=None, extra={},
                    )
                )
            )
    return bom


def python_bom(
    root: pathlib.Path, *, add: Optional[List[pathlib.Path]] = None
):
    for path in root.glob("setup.py"):
        setup_kwargs = SetupPyKWArg.get_kwargs(str(path))
        requirements = setup_kwargs.get("install_requires", [])
        if requirements:
            return python_requirements_to_bom(requirements)
    for path in root.glob("requirements.txt"):
        return python_requirements_to_bom(
            list(filter(bool, path.read_text().split("\n")))
        )
