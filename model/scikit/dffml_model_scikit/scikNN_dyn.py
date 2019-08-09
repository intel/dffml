# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import sys
import inspect
from collections import namedtuple
from typing import Dict

from sklearn.neighbors import KNeighborsClassifier

from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entry_point
from dffml_model_scikit.scikitbase import Scikit, ScikitContext


def kNN_applicable_features(self, features):
    usable = []
    for feature in features:
        if feature.dtype() != int and feature.dtype() != float:
            raise ValueError("kNN only supports int or float feature")
        if feature.length() != 1:
            raise ValueError(
                "kNN only supports single values (non-matrix / array)"
            )
        usable.append(feature.NAME)
    return sorted(usable)


# TODO modify config_get to raise an error if NoDefaultValue would be the return
# value of config_get
class NoDefaultValue:
    pass


# [(entry_point_name (command line usage), class name, scikit class, applicable_features_function]
for entry_point_name, name, cls, applicable_features_function in [
    ("scikitknn", "kNN", KNeighborsClassifier, kNN_applicable_features)
]:

    # Create the config namedtuple
    parameters = inspect.signature(cls).parameters
    defaults = [
        os.path.join(
            os.path.expanduser("~"),
            ".cache",
            "dffml",
            f"scikit-{entry_point_name}",
        ),
        NoDefaultValue,
    ] + [
        param.default
        for name, param in parameters.items()
        if param.default != inspect._empty
    ]
    config = namedtuple(
        name + "ModelConfig",
        ["directory", "predict"]
        + [
            param.name
            for _, param in parameters.items()
            if param.default != inspect._empty
        ],
        defaults=defaults,
    )

    setattr(sys.modules[__name__], config.__qualname__, config)

    # Define args and config methods
    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(
            args,
            above,
            "directory",
            Arg(
                default=os.path.join(
                    os.path.expanduser("~"),
                    ".cache",
                    "dffml",
                    f"scikit-{entry_point_name}",
                ),
                help="Directory where state should be saved",
            ),
        )
        cls.config_set(
            args,
            above,
            "predict",
            Arg(type=str, help="Label or the value to be predicted"),
        )
        for _, param in inspect.signature(cls.SCIKIT_MODEL):
            # TODO if param.default is an array then Args needs to get a
            # nargs="+"
            self.config_set(
                args,
                above,
                param.name,
                Args(
                    type=param.annotation,
                    default=NoDefaultValue
                    if param.default == inspect._empty
                    else param.default,
                ),
            )
        return args

    # -models feature1=scikitknn feature2=scikitknn
    # -model-feature1-predict feed -> feature1_model = kNNModel(kNNModelConfig(predict="face"))
    # -model-feature2-predict face -> feature2_model = kNNModel(kNNModelConfig(predict="face"))
    @classmethod
    def config(cls, config, *above):
        params = dict(
            directory=cls.config_get(config, above, "directory"),
            predict=cls.config_get(config, above, "predict"),
        )
        for name, _ in inspect.signature(self.SCIKIT_MODEL):
            params[name] = self.config_get(args, above, name)
        return cls.CONFIG(**params)

    dffml_cls_ctx = type(
        name + "ModelContext",
        (ScikitContext,),
        {"applicable_features": applicable_features_function},
    )

    dffml_cls = type(
        name + "Model",
        (Scikit,),
        {
            "CONFIG": config,
            "CONTEXT": dffml_cls_ctx,
            "SCIKIT_MODEL": cls,
            "args": args,
            "config": config,
        },
    )
    # Add the ENTRY_POINT_ORIG_LABEL
    dffml_cls = entry_point(entry_point_name)(dffml_cls)

    setattr(sys.modules[__name__], dffml_cls_ctx.__qualname__, dffml_cls_ctx)
    setattr(sys.modules[__name__], dffml_cls.__qualname__, dffml_cls)
