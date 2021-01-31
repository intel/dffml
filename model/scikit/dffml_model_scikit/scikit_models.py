# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import os
import sys
import pathlib

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
    RandomForestRegressor,
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


from dffml.base import field
from dffml.util.config.numpy import make_config_numpy
from dffml.util.entrypoint import entrypoint
from dffml.feature.feature import Feature, Features
from dffml_model_scikit.scikit_base import (
    Scikit,
    ScikitContext,
    ScikitUnsprvised,
    ScikitContextUnsprvised,
)


supervised_estimators = ["classifier", "regressor"]
unsupervised_estimators = ["clusterer"]
for entry_point_name, name, cls in [
    ("scikitknn", "KNeighborsClassifier", KNeighborsClassifier,),
    ("scikitadaboost", "AdaBoostClassifier", AdaBoostClassifier,),
    ("scikitsvc", "SVC", SVC),
    ("scikitgpc", "GaussianProcessClassifier", GaussianProcessClassifier,),
    ("scikitdtc", "DecisionTreeClassifier", DecisionTreeClassifier,),
    ("scikitrfc", "RandomForestClassifier", RandomForestClassifier,),
    ("scikitrfr", "RandomForestRegressor", RandomForestRegressor,),
    ("scikitmlp", "MLPClassifier", MLPClassifier),
    ("scikitgnb", "GaussianNB", GaussianNB),
    (
        "scikitqda",
        "QuadraticDiscriminantAnalysis",
        QuadraticDiscriminantAnalysis,
    ),
    ("scikitlr", "LinearRegression", LinearRegression),
    ("scikitlor", "LogisticRegression", LogisticRegression,),
    ("scikitgbc", "GradientBoostingClassifier", GradientBoostingClassifier,),
    ("scikitetc", "ExtraTreesClassifier", ExtraTreesClassifier,),
    ("scikitbgc", "BaggingClassifier", BaggingClassifier),
    ("scikiteln", "ElasticNet", ElasticNet),
    ("scikitbyr", "BayesianRidge", BayesianRidge),
    ("scikitlas", "Lasso", Lasso),
    ("scikitard", "ARDRegression", ARDRegression),
    ("scikitrsc", "RANSACRegressor", RANSACRegressor),
    ("scikitbnb", "BernoulliNB", BernoulliNB),
    ("scikitmnb", "MultinomialNB", MultinomialNB),
    ("scikitlda", "LinearDiscriminantAnalysis", LinearDiscriminantAnalysis),
    ("scikitdtr", "DecisionTreeRegressor", DecisionTreeRegressor),
    ("scikitgpr", "GaussianProcessRegressor", GaussianProcessRegressor),
    ("scikitomp", "OrthogonalMatchingPursuit", OrthogonalMatchingPursuit),
    ("scikitridge", "Ridge", Ridge),
    ("scikitlars", "Lars", Lars),
    ("scikitkmeans", "KMeans", KMeans),
    ("scikitbirch", "Birch", Birch),
    ("scikitmbkmeans", "MiniBatchKMeans", MiniBatchKMeans),
    ("scikitap", "AffinityPropagation", AffinityPropagation),
    ("scikims", "MeanShift", MeanShift),
    ("scikitsc", "SpectralClustering", SpectralClustering),
    ("scikitac", "AgglomerativeClustering", AgglomerativeClustering),
    ("scikitoptics", "OPTICS", OPTICS),
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
                "True cluster label for evaluating clustering models",
                default=None,
            ),
        )
    dffml_config_properties = {
        **{
            "directory": (
                pathlib.Path,
                field("Directory where state should be saved",),
            ),
            "features": (Features, field("Features to train on")),
        },
        **config_fields,
    }

    if estimator_type in unsupervised_estimators:
        dffml_config_properties["predict"] = (
            Feature,
            field(
                "Name used as meaning of prediction",
                default=Feature(name="cluster", dtype=str, length=1),
            ),
        )

    dffml_config = make_config_numpy(
        name + "ModelConfig", cls, properties=dffml_config_properties
    )

    dffml_cls_ctx = type(name + "ModelContext", (parentContext,), {},)

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
