# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import sys
import json
import hashlib
import inspect
from pathlib import Path
from typing import Tuple, Any, Callable, List, Dict, Optional, Type

from vowpalwabbit.sklearn_vw import VW

from dffml.repo import Repo
from dffml.base import config
from dffml.accuracy import Accuracy
from dffml.source.source import Sources
from dffml.base import make_config, field
from dffml.util.entrypoint import entrypoint
from dffml.util.cli.parser import list_action
from dffml.model.model import ModelContext, Model
from dffml.feature.feature import Feature, Features, DefFeature
from dffml.util.config.numpy import (
    numpy_get_default,
    numpy_cleanup_description,
    NUMPY_DOCS_TYPE_MAP,
)

from .vw_base import VWModel, VWContext


def vw_doc_to_field(type_str, description, param):
    default = param.default
    if default is inspect.Parameter.empty:
        default = numpy_get_default(type_str)

    type_cls = Any

    type_split = list(
        map(lambda x: x.lower(), type_str.replace(")", "").split())
    )
    for numpy_type_name, python_type in NUMPY_DOCS_TYPE_MAP.items():
        if numpy_type_name in type_split:
            type_cls = python_type

    if type_cls == Any and default != None:
        type_cls = type(default)

    return type_cls, field(description, default=default)


def vw_docstring_args(cls: Callable):
    parameters = inspect.signature(cls).parameters
    docstring = inspect.getdoc(cls.__init__)
    docparams = {}

    # Parse parameters and their datatypes from docstring
    # TODO clean description properly
    info_part = None
    des_part = None
    complete_description = []
    for line in docstring.split("\n"):
        if not ":" in line and info_part:
            if complete_description:
                if not complete_description[-1:] == "":
                    complete_description.append(line.strip())
            continue
        if info_part:
            if "," in info_part:
                param_name, info_part = info_part.split(",")
            if "(" in info_part:
                param_name, dtypes = info_part.split("(", maxsplit=1)
            else:
                param_name, dtypes = info_part, "bool"
            param_name = param_name.strip()
            dtypes = dtypes.strip()
            if param_name in parameters and param_name not in docparams:
                docparams[param_name] = [dtypes, []]
                docparams[param_name][1] = numpy_cleanup_description(
                    dtypes, complete_description
                )
        if ":" in line:
            complete_description.clear()
            info_part, des_part = line.split(":", maxsplit=1)
            complete_description.append(des_part)

    # Ensure all required parameters are present in docstring
    for param_name, param in parameters.items():
        if param_name in ["args", "kwargs"]:
            continue
        if not param_name in docparams:
            # TODO parameters 'rank', 'lrq', 'lrqdropout', 'probabilities', 'no_stdin'
            # not present in docstring.
            continue
        docparams[param_name] = vw_doc_to_field(*docparams[param_name], param)

    return docparams


def make_config_vw(
    name: str,
    cls: Type,
    properties: Optional[Dict[str, Tuple[Type, field]]] = None,
):
    if properties is None:
        properties = {}

    # overwrite default values of parsed parameters by applicable_config
    parsed_args = vw_docstring_args(cls)
    for key, value in properties.items():
        if key in parsed_args:
            parsed_args[key][1].default = properties[key][1].default
        parsed_args[key] = value

    return make_config(
        name,
        [tuple([key] + list(value)) for key, value in parsed_args.items()],
    )


def applicable_features(self, features):
    usable = []
    for feature in features:
        if feature.dtype() != int and feature.dtype() != float:
            raise ValueError("Models only supports int or float feature")
        if feature.length() != 1:
            raise ValueError(
                "Models only supports single values (non-matrix / array)"
            )
        usable.append(feature.NAME)
    return sorted(usable)


def custom_args_to_field(custom_args: Dict[str, Any]):
    if not custom_args:
        return custom_args
    for key, value in custom_args.items():
        custom_args[key] = type(value), field(key, default=value)
    return custom_args


VWCustomConfig = {}
# TODO add config for specific models like
VWPoissonRegressorConfig = {
    "b": 2,
    "loss_function": "poisson",
    "l": 0.1,
}
for (
    entry_point_name,
    name,
    applicable_config,
    applicable_features_function,
) in [
    ("VWCustom", "VWCustom", VWCustomConfig, applicable_features),
    (
        "VWPoissonRegressor",
        "VWPoissonRegressor",
        VWPoissonRegressorConfig,
        applicable_features,
    ),
]:

    dffml_config_properties = {
        **{
            "directory": (
                str,
                field(
                    "Directory where state and readable model should be saved",
                    default=os.path.join(
                        os.path.expanduser("~"),
                        ".cache",
                        "dffml",
                        f"vw-{entry_point_name}",
                    ),
                ),
            ),
            "features": (Features, field("Features to train on")),
            "predict": (Feature, field("Label or the value to be predicted"),),
        },
        **custom_args_to_field(applicable_config),
    }

    dffml_config = make_config_vw(
        name + "ModelConfig", VW, properties=dffml_config_properties
    )
    dffml_cls_ctx = type(
        name + "ModelContext",
        (VWContext,),
        {"applicable_features": applicable_features_function},
    )

    dffml_cls = type(
        name + "Model",
        (VWModel,),
        {"CONFIG": dffml_config, "CONTEXT": dffml_cls_ctx, "VW_MODEL": VW,},
    )
    dffml_cls = entrypoint(entry_point_name)(dffml_cls)

    setattr(sys.modules[__name__], dffml_config.__qualname__, dffml_config)
    setattr(sys.modules[__name__], dffml_cls_ctx.__qualname__, dffml_cls_ctx)
    setattr(sys.modules[__name__], dffml_cls.__qualname__, dffml_cls)
