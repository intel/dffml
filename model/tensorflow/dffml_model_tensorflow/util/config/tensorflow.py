"""
This file handles converting callables with tensorflow docstrings into config classes
by parsing their docstrings to find their default values, finding the help text
for each value, and then calling ``make_config`` to create a config class
representing the arguments to that callable.
"""
import inspect
import dataclasses

from typing import Dict, Optional, Tuple, Type, Any, Callable, List
import ast
from shlex import shlex
import tensorflow as tf

from dffml.base import make_config, field
from dffml.util.config.exceptions import ParameterNotInDocString


# Things people name their types mapped their real python types.
TENSORFLOW_DOCS_TYPE_MAP = {
    "int": int,
    "Integer": int,
    "integer": int,
    "str": str,
    "string": str,
    "String": str,
    "float": float,
    "Float": float,
    "dict": dict,
    "Dict": dict,
    "bool": bool,
    "Bool": bool,
    "Boolean": bool,
    "boolean": bool,
    "function": str,
}


def tensorflow_get_default(type_str):
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


def tensorflow_doc_to_field(type_str, description, param):
    default = param.default
    if default is inspect.Parameter.empty:
        default = tensorflow_get_default(type_str)

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
        for (
            tensorflow_type_name,
            python_type,
        ) in TENSORFLOW_DOCS_TYPE_MAP.items():
            if tensorflow_type_name in type_split:
                type_cls = python_type

    if type_cls == Any and default != None:
        type_cls = type(default)

    return type_cls, field(description, default=default)


def tensorflow_cleanup_description(
    dtypes, description_lines, last: bool = False
):
    if description_lines:
        # Remove the section header if we're on the last argument (since we will
        # have the title of it in the body of the last arguments description
        # currently).
        if last:
            description_lines = description_lines[:-1]
        # Get rid of any leading blank lines
        while description_lines[0] == "":
            description_lines = description_lines[1:]
        # Get rid of any trailing blank lines
        while description_lines[-1] == "":
            description_lines = description_lines[:-1]
        # Set the description to be the joined lines
        return " ".join(description_lines)
    return dtypes


def tensorflow_docstring_args(cls: Callable):
    """
    Given a tensorflow class, read its docstring and ``__init__`` parameters to
    generate a config class with properties containing the correct types,
    and default values.
    """
    parameters = inspect.signature(cls).parameters
    docstring = inspect.getdoc(cls)
    docparams = {}

    # Parse parameters and their datatypes from docstring
    last_param_name = None
    for line in docstring.split("\n"):
        if not ":" in line:
            if last_param_name:
                docparams[last_param_name][1].append(line.strip())
            continue
        param_name, dtypes = line.split(":", maxsplit=1)
        param_name = param_name.strip()
        dtypes = dtypes.strip()
        if last_param_name:
            if not dtypes:
                docparams[last_param_name][1] = tensorflow_cleanup_description(
                    dtypes, docparams[last_param_name][1], last=True
                )
                break
        if not param_name in parameters or param_name in docparams:
            continue
        docparams[param_name] = [dtypes, [dtypes]]
        if last_param_name:
            docparams[last_param_name][1] = tensorflow_cleanup_description(
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
        docparams[param_name] = tensorflow_doc_to_field(
            *docparams[param_name], param
        )

    return docparams


# TODO Just for now, remove once config is done
def parse_layers(input_layers: List[str]):
    """
    Given a list of tf.keras.layers as strings, instantiate them with input parameters.
    """
    all_layers = dict(inspect.getmembers(tf.keras.layers, inspect.isclass))
    live_layers = []

    for layer in input_layers:
        param_dict = {}
        layer_params_dict = {}

        layer_name, layer_params = layer.split("(", maxsplit=1)
        layer_params = layer_params.rsplit(")", 1)[0]
        if layer_params.strip():
            layer_params = "".join(text.strip() for text in list(layer_params))
            layer_params = (
                layer_params.replace(")", ")/")
                .replace("(", "/(")
                .replace("[", "/[")
                .replace("]", "]/")
            )

            lexer = shlex(layer_params, posix=True)
            lexer.whitespace = ","
            lexer.quotes = "/"
            for wordchar in ["=", "'", '"', ".", "-"]:
                lexer.wordchars += wordchar

            for word in lexer:
                key, value = word.split("=")
                layer_params_dict[key.strip()] = (
                    value.replace("'", "").replace('"', "").strip()
                )

            parsed_args = tensorflow_docstring_args(all_layers[layer_name])

            for key, value in layer_params_dict.items():
                dtype, _ = parsed_args[key]
                try:
                    if value in ["True", "False", "None"]:
                        value = ast.literal_eval(value)
                    else:
                        value = dtype(value)
                except (TypeError, ValueError):
                    # handles tuple, list
                    try:
                        value = ast.literal_eval(value)
                    except:
                        value = str(value)
                param_dict[key] = value
        live_layers.append(
            tf.keras.layers.deserialize(
                {"class_name": layer_name, "config": param_dict}
            )
        )
    return live_layers


def make_config_tensorflow(
    name: str,
    cls: Type,
    properties: Optional[Dict[str, Tuple[Type, field]]] = None,
):
    """
    Given a tensorflow class, read its docstring and ``__init__`` parameters to
    generate a config class with properties containing the correct types,
    and default values.
    """
    if properties is None:
        properties = {}
    doc_params = tensorflow_docstring_args(cls)
    properties.update(doc_params)

    return make_config(
        name, [tuple([key] + list(value)) for key, value in properties.items()]
    )
