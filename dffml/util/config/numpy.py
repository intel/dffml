"""
This file handles converting callables with numpy docstrings into config classes
by parsing their docstrings to find their default values, finding the help text
for each value, and then calling ``make_config`` to create a config class
representing the arguments to that callable.
"""
import inspect
import dataclasses
from typing import Dict, Optional, Tuple, Type, Any, Callable

from dffml.base import make_config, field

from .exceptions import ParameterNotInDocString


# Things people name their types mapped their real python types.
NUMPY_DOCS_TYPE_MAP = {
    "int": int,
    "integer": int,
    "str": str,
    "string": str,
    "float": float,
    "dict": dict,
    "bool": bool,
}


def numpy_get_default(type_str):
    if not "default" in type_str:
        return dataclasses.MISSING
    type_str = type_str[type_str.index("default") :]
    type_str = type_str.replace("default", "")
    type_str = type_str.replace(")", "")
    type_str = type_str.replace("=", "")
    type_str = type_str.replace('"', "")
    type_str = type_str.replace("'", "")
    type_str = type_str.strip()
    if type_str == "None":
        return None
    return type_str


def numpy_doc_to_field(type_str, description, param):
    default = param.default
    if default is inspect.Parameter.empty:
        default = numpy_get_default(type_str)

    type_cls = Any

    # Set of choices
    if "{'" in type_str and "'}" in type_str:
        type_cls = str
    elif "{" in type_str and "}" in type_str:
        type_cls = int
        if "." in type_str:
            type_cls = float
    else:
        type_split = list(
            map(lambda x: x.lower(), type_str.replace(",", "").split())
        )
        for numpy_type_name, python_type in NUMPY_DOCS_TYPE_MAP.items():
            if numpy_type_name in type_split:
                type_cls = python_type

    if type_cls == Any and default != None:
        type_cls = type(default)

    return type_cls, field(description, default=default)


def numpy_cleanup_description(dtypes, description_lines, last: bool = False):
    if description_lines:
        # Remove the section header if we're on the last argument (since we will
        # have the title of it in the body of the last arguments description
        # currently).
        if last:
            description_lines = description_lines[:-1]
        # Get rid of any leading blank lines
        while description_lines and description_lines[0] == "":
            description_lines = description_lines[1:]
        # Get rid of any trailing blank lines
        while description_lines and description_lines[-1] == "":
            description_lines = description_lines[:-1]
        # Set the description to be the joined lines
        return " ".join(description_lines)
    return dtypes


def numpy_docstring_args(cls: Callable):
    parameters = inspect.signature(cls).parameters
    docstring = inspect.getdoc(cls)
    docparams = {}

    # Parse parameters and their datatypes from docstring
    last_param_name = None
    for line in docstring.split("\n"):
        if not ":" in line:
            if last_param_name:
                if line.startswith("--"):
                    docparams[last_param_name][1] = numpy_cleanup_description(
                        dtypes, docparams[last_param_name][1], last=True
                    )
                    break
                # Append description lines
                docparams[last_param_name][1].append(line.strip())
            continue
        param_name, dtypes = line.split(":", maxsplit=1)
        param_name = param_name.strip()
        dtypes = dtypes.strip()
        if not param_name in parameters or param_name in docparams:
            continue
        docparams[param_name] = [dtypes, []]
        if last_param_name:
            docparams[last_param_name][1] = numpy_cleanup_description(
                dtypes, docparams[last_param_name][1]
            )
        last_param_name = param_name

    # Ensure all required parameters are present in docstring
    for param_name, param in parameters.items():
        if param_name in ["args", "kwargs"]:
            continue
        if not param_name in docparams:
            raise ParameterNotInDocString(
                f"{param_name} for {cls.__qualname__}"
            )
        docparams[param_name] = numpy_doc_to_field(
            *docparams[param_name], param
        )

    return docparams


def make_config_numpy(
    name: str,
    cls: Type,
    properties: Optional[Dict[str, Tuple[Type, field]]] = None,
):
    """
    Given a numpy class, read its docstring and ``__init__`` parameters to
    generate a config class with properties containing the correct types,
    and default values.
    """
    if properties is None:
        properties = {}

    properties.update(numpy_docstring_args(cls))

    return make_config(
        name, [tuple([key] + list(value)) for key, value in properties.items()]
    )
