# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import sys
import ast
import inspect
from collections import namedtuple
from typing import Dict

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import (
    GaussianProcessClassifier,
    GaussianProcessRegressor,
)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestClassifier,
    AdaBoostClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    BaggingClassifier,
)
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB
from sklearn.discriminant_analysis import (
    QuadraticDiscriminantAnalysis,
    LinearDiscriminantAnalysis,
)
from sklearn.linear_model import (
    LinearRegression,
    LogisticRegression,
    ElasticNet,
    BayesianRidge,
    Lasso,
    ARDRegression,
    RANSACRegressor,
    OrthogonalMatchingPursuit,
    Lars,
)

from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entry_point
from dffml_model_scikit.scikit_base import Scikit, ScikitContext

from dffml.feature.feature import Feature, Features
from dffml.util.cli.parser import list_action


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


# TODO modify config_get to raise an error if NoDefaultValue would be the return
# value of config_get
class NoDefaultValue:
    pass


for entry_point_name, name, cls, applicable_features_function in [
    (
        "scikitknn",
        "KNeighborsClassifier",
        KNeighborsClassifier,
        applicable_features,
    ),
    (
        "scikitadaboost",
        "AdaBoostClassifier",
        AdaBoostClassifier,
        applicable_features,
    ),
    ("scikitsvc", "SVC", SVC, applicable_features),
    (
        "scikitgpc",
        "GaussianProcessClassifier",
        GaussianProcessClassifier,
        applicable_features,
    ),
    (
        "scikitdtc",
        "DecisionTreeClassifier",
        DecisionTreeClassifier,
        applicable_features,
    ),
    (
        "scikitrfc",
        "RandomForestClassifier",
        RandomForestClassifier,
        applicable_features,
    ),
    ("scikitmlp", "MLPClassifier", MLPClassifier, applicable_features),
    ("scikitgnb", "GaussianNB", GaussianNB, applicable_features),
    (
        "scikitqda",
        "QuadraticDiscriminantAnalysis",
        QuadraticDiscriminantAnalysis,
        applicable_features,
    ),
    ("scikitlr", "LinearRegression", LinearRegression, applicable_features),
    (
        "scikitlor",
        "LogisticRegression",
        LogisticRegression,
        applicable_features,
    ),
    (
        "scikitgbc",
        "GradientBoostingClassifier",
        GradientBoostingClassifier,
        applicable_features,
    ),
    (
        "scikitetc",
        "ExtraTreesClassifier",
        ExtraTreesClassifier,
        applicable_features,
    ),
    (
        "scikitbgc",
        "BaggingClassifier",
        BaggingClassifier,
        applicable_features,
    ),
    ("scikiteln", "ElasticNet", ElasticNet, applicable_features,),
    ("scikitbyr", "BayesianRidge", BayesianRidge, applicable_features,),
    ("scikitlas", "Lasso", Lasso, applicable_features,),
    ("scikitard", "ARDRegression", ARDRegression, applicable_features),
    ("scikitrsc", "RANSACRegressor", RANSACRegressor, applicable_features),
    ("scikitbnb", "BernoulliNB", BernoulliNB, applicable_features),
    ("scikitmnb", "MultinomialNB", MultinomialNB, applicable_features),
    (
        "scikitlda",
        "LinearDiscriminantAnalysis",
        LinearDiscriminantAnalysis,
        applicable_features,
    ),
    (
        "scikitdtr",
        "DecisionTreeRegressor",
        DecisionTreeRegressor,
        applicable_features,
    ),
    (
        "scikitgpr",
        "GaussianProcessRegressor",
        GaussianProcessRegressor,
        applicable_features,
    ),
    (
        "scikitomp",
        "OrthogonalMatchingPursuit",
        OrthogonalMatchingPursuit,
        applicable_features,
    ),
    ("scikitlars", "Lars", Lars, applicable_features),
]:

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
    dffml_config = namedtuple(
        name + "ModelConfig",
        ["directory", "predict", "features"]
        + [
            param.name
            for _, param in parameters.items()
            if param.default != inspect._empty
        ],
        defaults=defaults,
    )

    setattr(sys.modules[__name__], dffml_config.__qualname__, dffml_config)

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

        cls.config_set(
            args,
            above,
            "features",
            Arg(
                nargs="+",
                required=True,
                type=Feature.load,
                action=list_action(Features),
                help="Features to train on",
            ),
        )

        for param in inspect.signature(cls.SCIKIT_MODEL).parameters.values():
            # TODO if param.default is an array then Args needs to get a
            # nargs="+"
            cls.config_set(
                args,
                above,
                param.name,
                Arg(
                    type=cls.type_for(param),
                    default=NoDefaultValue
                    if param.default == inspect._empty
                    else param.default,
                ),
            )
        return args

    @classmethod
    def config(cls, config, *above):
        params = dict(
            directory=cls.config_get(config, above, "directory"),
            predict=cls.config_get(config, above, "predict"),
            features=cls.config_get(config, above, "features"),
        )
        for name in inspect.signature(cls.SCIKIT_MODEL).parameters.keys():
            params[name] = cls.config_get(config, above, name)
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
            "CONFIG": dffml_config,
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
