import sys
import functools
import dataclasses

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    top_k_accuracy_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    jaccard_score,
    roc_auc_score,
    adjusted_mutual_info_score,
    adjusted_rand_score,
    completeness_score,
    fowlkes_mallows_score,
    homogeneity_score,
    mutual_info_score,
    normalized_mutual_info_score,
    rand_score,
    v_measure_score,
    explained_variance_score,
    max_error,
    mean_absolute_error,
    mean_squared_error,
    mean_squared_log_error,
    median_absolute_error,
    r2_score,
    mean_poisson_deviance,
    mean_gamma_deviance,
    mean_absolute_percentage_error,
)

from dffml.util.entrypoint import entrypoint
from dffml.base import make_config
from dffml.util.config.numpy import numpy_docstring_args

from dffml_model_scikit.scikit_scorer_base import (
    ScikitScorer,
    ScikitScorerContext,
)


for entrypoint_name, name, method in (
    ("acscore", "AccuracyScore", accuracy_score,),
    ("bacscore", "BalancedAccuracyScore", balanced_accuracy_score,),
    ("topkscore", "TopKAccuracyScore", top_k_accuracy_score,),
    ("avgprescore", "AveragePrecisionScore", average_precision_score,),
    ("brierscore", "BrierScoreLoss", brier_score_loss,),
    ("f1score", "F1Score", f1_score,),
    ("logloss", "LogLoss", log_loss,),
    ("prescore", "PrecisionScore", precision_score,),
    ("recallscore", "RecallScore", recall_score,),
    ("jacscore", "JaccardScore", jaccard_score,),
    ("rocaucscore", "RocAucScore", roc_auc_score,),
    (
        "adjmutinfoscore",
        "AdjustedMutualInfoScore",
        adjusted_mutual_info_score,
    ),
    ("adjrandscore", "AdjustedRandScore", adjusted_rand_score,),
    ("complscore", "CompletenessScore", completeness_score,),
    ("fowlmalscore", "FowlkesMallowsScore", fowlkes_mallows_score,),
    ("homoscore", "HomogeneityScore", homogeneity_score,),
    ("mutinfoscore", "MutualInfoScore", mutual_info_score,),
    (
        "normmutinfoscore",
        "NormalizedMutualInfoScore",
        normalized_mutual_info_score,
    ),
    ("randscore", "RandScore", rand_score,),
    ("vmscore", "VMeasureScore", v_measure_score,),
    ("exvscore", "ExplainedVarianceScore", explained_variance_score,),
    ("maxerr", "MaxError", max_error,),
    ("meanabserr", "MeanAbsoluteError", mean_absolute_error,),
    ("meansqrerr", "MeanSquaredError", mean_squared_error,),
    ("meansqrlogerr", "MeanSquaredLogError", mean_squared_log_error,),
    ("medabserr", "MedianAbsoluteError", median_absolute_error,),
    ("r2score", "R2Score", r2_score,),
    ("meanpoidev", "MeanPoissonDeviance", mean_poisson_deviance,),
    ("meangammadev", "MeanGammaDeviance", mean_gamma_deviance,),
    (
        "meanabspererr",
        "MeanAbsolutePercentageError",
        mean_absolute_percentage_error,
    ),
):
    parentContext = ScikitScorerContext
    parentScorer = ScikitScorer

    # Custom config for some scorers where when writing tests we found that the
    # default pos_label is 1. If you are doing binary classification you have to
    # do 1. If you are doing multiple classification you should use 2 or 4. We
    # override that default value of 1 to 2 so that we can support multiclass
    # classification.
    # References:
    # - https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html#sklearn.metrics.average_precision_score
    properties = numpy_docstring_args(method)
    if name in (
        "RecallScore",
        "PrecisionScore",
        "JaccardScore",
        "F1Score",
        "AveragePrecisionScore",
    ):
        properties["pos_label"][1].default = 2
    # We remove any config property without a default value. These are always
    # the first two arguments to the method, which will be provided by
    # ScikitScorerContext.score().
    for property_to_remove in [
        key
        for key, (_, field) in properties.items()
        if field.default is dataclasses.MISSING
    ]:
        del properties[property_to_remove]

    dffml_cls_ctx = type(name + "ScorerContext", (parentContext,), {},)

    dffml_cls = type(
        name + "Scorer",
        (parentScorer,),
        {
            "CONTEXT": dffml_cls_ctx,
            "CONFIG": make_config(
                name + "Config",
                [
                    tuple([key] + list(value))
                    for key, value in properties.items()
                ],
            ),
            "SCIKIT_SCORER": functools.partial(method),
        },
    )
    # Add the ENTRY_POINT_ORIG_LABEL
    dffml_cls = entrypoint(entrypoint_name)(dffml_cls)

    setattr(sys.modules[__name__], dffml_cls_ctx.__qualname__, dffml_cls_ctx)
    setattr(sys.modules[__name__], dffml_cls.__qualname__, dffml_cls)
