"""
Python specific helper functions
"""
import types
import pathlib
import importlib
from typing import Optional, Callable, Union, Tuple, Iterator


def modules(
    root: Union[str, pathlib.Path],
    package_name: str,
    *,
    skip: Optional[Callable[[str, pathlib.Path], bool]] = None,
) -> Iterator[Tuple[str, types.ModuleType]]:
    """
    Import all modules (Python files) starting at the directory given by
    ``root`` of the package ``package_name``.

    Parameters
    ----------
    root : str, pathlib.Path
        The path to the directory containing the top level ``__init__.py`` of
        the package.
    package_name : str
        Top level package name of the package your importing. There are no ``.``
        characters in this. For example, ``dffml``, or ``dffml_config_yaml``.
    skip : callable, optional
        Function that will be called with ``(import_name, path)`` and should
        return a boolean, True if the module should not be imported and yielded
        to the caller. If it returns False, the Python file at ``path`` within
        ``package_name`` will be imported by passing ``import_name`` to
        :py:func`importlib.import_module`.

    Yields
    ------
    import_name : str
        The ``package_name.subdir.file_stem`` used to import the module.
    module : types.ModuleType
        The imported module.

    Examples
    --------

    You can get all the Python files imported individually in a package as
    follows.

    >>> import dffml
    >>> import pathlib
    >>> import importlib
    >>>
    >>> package_name = "xml"
    >>> top_level_module = importlib.import_module(package_name)
    >>>
    >>> root = pathlib.Path(top_level_module.__path__[0])
    >>>
    >>> # Skip any files in dom/ subdirectory and __main__.py and __init__.py
    >>> def skip(_import_name, path) -> bool:
    ...     return (root / "dom") in path.parents or path.name.startswith("__")
    ...
    >>> # Print the first module
    >>> for import_name, module in dffml.modules(root, package_name, skip=skip):
    ...     print(import_name)
    ...     break
    ...
    xml.sax.expatreader
    """
    for path in pathlib.Path(root).rglob("*.py"):
        # Figure out name
        import_name = pathlib.Path(str(path)[len(str(root)) :]).parts[1:]
        import_name = (
            package_name
            + "."
            + ".".join(
                list(import_name[:-1]) + [import_name[-1].replace(".py", "")]
            )
        )
        # Check if we should skip importing this file
        if skip and skip(import_name, path):
            continue
        # Import module
        yield import_name, importlib.import_module(import_name)
