"""
Python specific helper functions
"""
import sys
import types
import pathlib
import inspect
import importlib
from typing import Callable, Iterator, Optional, Tuple, Union, ForwardRef


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
    xml.etree.ElementInclude
    """
    for path in sorted(pathlib.Path(root).rglob("*.py")):
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


# See comment at beginning of within_method()
IN_IPYTHON = False
CHECKED_IN_IPYTHON = False
IPYTHON_INSPECT_PATCHED = False


def within_method(obj: object, method_name: str, max_depth: int = -1) -> bool:
    """
    Return True if a caller is being called from a given method of a given
    object.

    Parameters
    ----------
    obj : object
        Check if we are within a method of this object.
    method_name : str
        Check if we are within a method by this name.
    max_depth : int, optional (-1)
        Stop checking stack frames after we have checked this many.

    Returns
    -------
    within : boolean
        True if the calling function is being called from within the method
        given bound to the object given.

    Examples
    --------

    >>> from dffml import within_method
    >>>
    >>> class FirstClass:
    ...     def feedface(self):
    ...         print(within_method(self, "__init__", max_depth=3))
    ...
    >>> first = FirstClass()
    >>> first .feedface()
    False
    >>>
    >>> class SecondClass(FirstClass):
    ...     def __init__(self):
    ...         self.feedface()
    ...
    >>> second = SecondClass()
    True
    >>>
    >>> class ThirdClass(SecondClass):
    ...     def __init__(self):
    ...         self.deadbeef()
    ...
    ...     def deadbeef(self):
    ...         self.feedface()
    ...
    >>> third = ThirdClass()
    False
    """
    # HACK Fix for if we are running in IPython notebook. Sometimes it doesn't
    # patch inspect.findsource as is intended
    # References:
    # - https://github.com/ipython/ipython/issues/1456
    # - https://github.com/ipython/ipython/commit/298fdab5025745cd25f7f48147d8bc4c65be9d4a#diff-3a77d00d5690f670e9ac680f06b8ffe7ca902c6d325673f32e719d8e55b11ae3R209
    global IN_IPYTHON
    global CHECKED_IN_IPYTHON
    global IPYTHON_INSPECT_PATCHED
    if (
        not CHECKED_IN_IPYTHON
        and sys.version_info.major == 3
        and sys.version_info.minor <= 7
    ):
        try:
            get_ipython()
            IN_IPYTHON = True
        except:
            pass
        CHECKED_IN_IPYTHON = True
        if IN_IPYTHON and not IPYTHON_INSPECT_PATCHED:
            import IPython.core.ultratb

            inspect.findsource = IPython.core.ultratb.findsource
            IPYTHON_INSPECT_PATCHED = False
    # Grab stack frames
    try:
        frames = inspect.stack()
    except ImportError:
        # HACK ImportError Fix for lazy_import rasing on autosklearn/smac: emcee
        return True
    for i, frame_info in enumerate(frames):
        if max_depth != -1 and i >= max_depth:
            break
        if (
            frame_info.function == method_name
            and "self" in frame_info.frame.f_locals
            and frame_info.frame.f_locals["self"] is obj
        ):
            return True
    return False


def is_forward_ref_dataclass(dataclass, type_cls):
    """
    Check if a field's type is a ForwardRef, either via being an instance, or
    being a type which is a string. An instance of a string is not a type,
    therefore if we see a string, we should assume it is a ForwardRef.
    """
    return isinstance(type_cls, (ForwardRef, str))


def resolve_forward_ref_dataclass(dataclass, type_cls):
    """
    >>> import dataclasses
    >>> import dffml
    >>>
    >>> @dataclasses.dataclass
    ... class MyClass:
    ...     a: "MyClass"
    >>>
    >>> dffml.resolve_forward_ref_dataclass(MyClass, list(dataclasses.fields(MyClass))[0].type)
    """
    if isinstance(type_cls, ForwardRef):
        # Grab the string version
        # See: https://github.com/python/cpython/pull/21553#discussion_r459034775
        type_cls = type_cls.__forward_arg__
    if dataclass is not None and type_cls == dataclass.__qualname__:
        # Handle special case where string type is the dataclass. When
        # an object is definined with a property whose type is the same
        # as the class being defined. Therefore object is not yet
        # defined within the scope of the object's definition. Therefore
        # we handle the special case by checking if the name is the
        # same.
        type_cls = dataclass
    else:
        # TODO Handle case where string is used that is not the same
        # class. This may require using ast.parse or just loading a
        # module via importlib and inspecting the global namespace. This
        # usually happens when a class which is used a property is
        # defined later within the same file.
        raise NotImplementedError(
            "No support for string types other than own class"
        )
