# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import sys

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
from dffml.util.config.numpy import make_config_numpy
from dffml.util.entrypoint import entrypoint
from dffml_model_scikit.scikit_base import (
    Scikit,
    ScikitContext,
    ScikitUnsprvised,
    ScikitContextUnsprvised,
)
from dffml.feature.feature import Feature, Features, DefFeature


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
    ("scikitbgc", "BaggingClassifier", BaggingClassifier, applicable_features),
    ("scikiteln", "ElasticNet", ElasticNet, applicable_features),
    ("scikitbyr", "BayesianRidge", BayesianRidge, applicable_features),
    ("scikitlas", "Lasso", Lasso, applicable_features),
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
    ("scikitridge", "Ridge", Ridge, applicable_features),
    ("scikitlars", "Lars", Lars, applicable_features),
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
            Feature,
            field("Label or the value to be predicted"),
        )
    elif estimator_type in unsupervised_estimators:
        parentContext = ScikitContextUnsprvised
        parentModel = ScikitUnsprvised
        config_fields["tcluster"] = (
            Feature,
            field(
                "True cluster labelfor evaluating clustering models",
                default=None,
            ),
        )
    dffml_config_properties = {
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
    }

    if estimator_type in unsupervised_estimators:
        dffml_config_properties["predict"] = (
            Feature,
            field(
                "field here for compability with other functions,no need to change",
                default=DefFeature(name="Prediction", dtype="str", length=10),
            ),
        )

    dffml_config = make_config_numpy(
        name + "ModelConfig", cls, properties=dffml_config_properties
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
