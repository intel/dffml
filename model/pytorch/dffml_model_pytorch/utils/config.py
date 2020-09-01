import inspect
from dffml.base import field, make_config
from typing import Callable, Optional, Dict, Tuple, Type


def inspect_pytorch_params(cls: Callable):
    parameters = inspect.signature(cls).parameters
    args = {}

    for param_name, param in parameters.items():
        args[param_name] = (
            param.annotation,
            field(
                param_name,
                default=param.default
                if param.default is not inspect.Parameter.empty
                else None,
            ),
        )

    return args


def make_pytorch_config(
    name: str,
    cls: Type,
    properties: Optional[Dict[str, Tuple[Type, field]]] = None,
):
    """
    Given a class or function, read its docstring and ``__init__`` parameters to
    generate a config class with properties containing the correct types,
    and default values.
    """
    if properties is None:
        properties = {}

    properties.update(inspect_pytorch_params(cls))

    return make_config(
        name, [tuple([key] + list(value)) for key, value in properties.items()]
    )
