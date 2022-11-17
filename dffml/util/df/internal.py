import types
import inspect

from ...df.base import op


def object_to_operations(obj, module=None):
    """
    Takes an object and creates a list of operations for that object, after
    wrapping any likely targets (functions, methods) with op.
    """
    if module is not None:
        if not inspect.ismodule(module):
            raise TypeError(f"{module} is not a module")
        python_path = f"{module.__name__}"
    elif inspect.ismodule(obj):
        return object_to_operations(obj, module=obj)
    else:
        python_path = f"{obj.__module__}.{obj.__qualname__}"
    if inspect.isfunction(obj):
        obj = types.SimpleNamespace(obj=obj)
    return [
        op(name=f"{python_path}:{name}")(method)
        if not hasattr(method, "imp")
        else method.imp
        for name, method in inspect.getmembers(
            obj,
            predicate=lambda i: inspect.ismethod(i)
            or inspect.isfunction(i)
            and not hasattr(i, "__supertype__")
            # NOTE HACK Fails in 3.9.13 to remove
            # NewType without the check in the str repr.
            and " NewType " not in str(i),
        )
    ]
