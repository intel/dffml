# The following code imports everything in dffml so that it can be accessed from
# the top level package
import sys
import inspect
import pathlib
import importlib
from typing import Optional, Callable


def modules(
    root: pathlib.Path,
    package_name: str,
    *,
    skip: Optional[Callable[[str, pathlib.Path], bool]] = None,
):
    for path in root.rglob("*.py"):
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


root = pathlib.Path(__file__).parent
skel = root / "skel"
cli = root / "cli"
package_name = __package__
# Skip any files in skel and __main__.py and __init__.py
skip = (
    lambda _import_name, path: skel in path.parents
    or cli in path.parents
    or path.name.startswith("__")
)

# All classes and functions
cls_func_all = {}


class DuplicateName(Exception):
    """
    Raised when two classes or functions defined in different files share the
    same name.
    """


# If a duplicate name is found, we specify which one to prefer here
DUPLICATE_PREFER = {
    "train": "high_level",
    "predict": "high_level",
    "accuracy": "high_level",
    "load": "high_level",
    "save": "high_level",
    "run": "high_level",
    "list_action": "base",
}
# List of modules not to expose
SKIP = ["cli", "util.cli.cmds", "util.testing.consoletest"]


for import_name, module in modules(root, package_name, skip=skip):
    import_name_no_package = import_name[len(package_name) + 1 :]
    # Check if we should skip this module
    if any(
        filter(lambda check: import_name_no_package.startswith(check), SKIP)
    ):
        continue
    # Iterate over all of the objects in the module
    for name, obj in inspect.getmembers(module):
        # Skip if not a class or function
        if (
            not hasattr(obj, "__module__")
            or not obj.__module__.startswith(import_name)
            or (not inspect.isclass(obj) and not inspect.isfunction(obj))
        ):
            continue
        fullname = obj.__module__ + "." + obj.__qualname__
        if obj.__qualname__ in cls_func_all:
            # Do not override prefered is already in cls_func_all, or if it's a
            # duplicate of itself (somehow this is possible that we see it from
            # the same module twice?)
            if cls_func_all[obj.__qualname__][1] == module:
                continue
            if name in DUPLICATE_PREFER:
                if cls_func_all[obj.__qualname__][0] == DUPLICATE_PREFER[name]:
                    continue
            else:
                raise DuplicateName(
                    f"{name} in both "
                    f"{cls_func_all[obj.__qualname__][0]} and "
                    f"{import_name_no_package}: "
                    f"(exists: {cls_func_all[obj.__qualname__][1]}, "
                    f"new: {module}) "
                )
        # Add to dict to ensure no duplicates
        cls_func_all[obj.__qualname__] = (import_name_no_package, module, obj)

for name, (_import_name, _module, obj) in cls_func_all.items():
    setattr(sys.modules[__name__], name, obj)

# Export everything
__all__ = list(cls_func_all.keys())
