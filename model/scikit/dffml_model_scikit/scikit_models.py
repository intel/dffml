# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import sys
import ast
import inspect
import dataclasses
from collections import namedtuple
from typing import Dict, Optional, Tuple, Type, Any

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
    Ridge,
)
from sklearn.cluster import (
    KMeans,
    Birch,
    MiniBatchKMeans,
    AffinityPropagation,
    MeanShift,
    SpectralClustering,
    AgglomerativeClustering,
    OPTICS,
)


from dffml.base import make_config, field
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entrypoint
from dffml_model_scikit.scikit_base import (
    Scikit,
    ScikitContext,
    ScikitUnsprvised,
    ScikitContextUnsprvised,
)
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


class ParameterNotInDocString(Exception):
    """
    Raised when a scikit class has a parameter in its ``__init__`` which was not
    present in it's docstring. Therefore we have no typing information for it.
    """


def scikit_get_default(type_str):
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


SCIKIT_DOCS_TYPE_MAP = {
    "int": int,
    "integer": int,
    "str": str,
    "string": str,
    "float": float,
    "dict": dict,
    "bool": bool,
}


def scikit_doc_to_field(type_str, param):
    default = param.default
    if default is inspect.Parameter.empty:
        default = scikit_get_default(type_str)

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
        for scikit_type_name, python_type in SCIKIT_DOCS_TYPE_MAP.items():
            if scikit_type_name in type_split:
                type_cls = python_type

    if type_cls == Any and default != None:
        type_cls = type(default)

    return type_cls, field(type_str, default=default)


def mkscikit_config_cls(
    name: str,
    cls: Type,
    properties: Optional[Dict[str, Tuple[Type, field]]] = None,
):
    """
    Given a scikit class, read its docstring and ``__init__`` parameters to
    generate a config class with properties containing the correct types,
    and default values.
    """
    if properties is None:
        properties = {}

    parameters = inspect.signature(cls).parameters
    docstring = inspect.getdoc(cls)
    docparams = {}

    # Parse parameters and their datatypes from docstring
    last_param_name = None
    for line in docstring.split("\n"):
        if not ":" in line:
            continue
        param_name, dtypes = line.split(":", maxsplit=1)
        param_name = param_name.strip()
        dtypes = dtypes.strip()
        if not param_name in parameters or param_name in docparams:
            continue
        docparams[param_name] = dtypes
        last_param_name = param_name

    # Ensure all required parameters are present in docstring
    for param_name, param in parameters.items():
        if param_name in ["args", "kwargs"]:
            continue
        if not param_name in docparams:
            raise ParameterNotInDocString(
                f"{param_name} for {cls.__qualname__}"
            )
        properties[param_name] = scikit_doc_to_field(
            docparams[param_name], param
        )

    return make_config(
        name, [tuple([key] + list(value)) for key, value in properties.items()]
    )


supervised_estimators = ["classifier", "regressor"]
unsupervised_estimators = ["clusterer"]
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
    ("scikitlr", "LinearRegression", LinearRegression, applicable_features,),
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
    ("scikiteln", "ElasticNet", ElasticNet, applicable_features),
    ("scikitbyr", "BayesianRidge", BayesianRidge, applicable_features,),
    ("scikitlas", "Lasso", Lasso, applicable_features,),
    ("scikitard", "ARDRegression", ARDRegression, applicable_features,),
    ("scikitrsc", "RANSACRegressor", RANSACRegressor, applicable_features,),
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
    ("scikitridge", "Ridge", Ridge, applicable_features,),
    ("scikitlars", "Lars", Lars, applicable_features,),
    ("scikitkmeans", "KMeans", KMeans, applicable_features),
    ("scikitbirch", "Birch", Birch, applicable_features),
    (
        "scikitmbkmeans",
        "MiniBatchKMeans",
        MiniBatchKMeans,
        applicable_features,
    ),
    (
        "scikitap",
        "AffinityPropagation",
        AffinityPropagation,
        applicable_features,
    ),
    ("scikims", "MeanShift", MeanShift, applicable_features),
    (
        "scikitsc",
        "SpectralClustering",
        SpectralClustering,
        applicable_features,
    ),
    (
        "scikitac",
        "AgglomerativeClustering",
        AgglomerativeClustering,
        applicable_features,
    ),
    ("scikitoptics", "OPTICS", OPTICS, applicable_features),
]:
    estimator_type = cls._estimator_type
    config_fields = dict()
    if estimator_type in supervised_estimators:
        parentContext = ScikitContext
        parentModel = Scikit
        config_fields["predict"] = (
            str,
            field("Label or the value to be predicted"),
        )
    elif estimator_type in unsupervised_estimators:
        parentContext = ScikitContextUnsprvised
        parentModel = ScikitUnsprvised
        config_fields["tcluster"] = (
            str,
            field(
                "True cluster labelfor evaluating clustering models",
                default=None,
            ),
        )
    dffml_config = mkscikit_config_cls(
        name + "ModelConfig",
        cls,
        properties={
            **{
                "directory": (
                    str,
                    field(
                        "Directory where state should be saved",
                        default=os.path.join(
                            os.path.expanduser("~"),
                            ".cache",
                            "dffml",
                            f"scikit-{entry_point_name}",
                        ),
                    ),
                ),
                "features": (Features, field("Features to train on")),
            },
            **config_fields,
        },
    )

    dffml_cls_ctx = type(
        name + "ModelContext",
        (parentContext,),
        {"applicable_features": applicable_features_function},
    )

    dffml_cls = type(
        name + "Model",
        (parentModel,),
        {
            "CONFIG": dffml_config,
            "CONTEXT": dffml_cls_ctx,
            "SCIKIT_MODEL": cls,
        },
    )
    # Add the ENTRY_POINT_ORIG_LABEL
    dffml_cls = entrypoint(entry_point_name)(dffml_cls)

    setattr(sys.modules[__name__], dffml_config.__qualname__, dffml_config)
    setattr(sys.modules[__name__], dffml_cls_ctx.__qualname__, dffml_cls_ctx)
    setattr(sys.modules[__name__], dffml_cls.__qualname__, dffml_cls)
