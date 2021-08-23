from typing import Union
from dffml.base import config
from dffml.util.entrypoint import entrypoint
from dffml.source.source import SourcesContext
from dffml.model import ModelContext, ModelNotTrained
from dffml.feature import Feature, Features
from dffml.accuracy import (
    AccuracyScorer,
    AccuracyContext,
)


class ScorerWillNotWork(Exception):
    pass


@config
class SklearnModelAccuracyConfig:
    pass


class SklearnModelAccuracyContext(AccuracyContext):
    """
    Default scorer for Sklearn Models.
    """

    async def score(
        self, mctx: ModelContext, sctx: SourcesContext, *features: Feature,
    ):
        if not mctx.parent.clf_path.is_file():
            raise ModelNotTrained("Train model before assessing for accuracy.")

        if mctx.parent.clf._estimator_type not in ("classifier", "regressor"):
            raise ScorerWillNotWork(
                "SklearnModelAccuracy will not work with Clustering Models"
            )
        is_multi = len(features) > 1
        if is_multi:
            predictions = [feature.name for feature in features]
        elif len(features) == 1:
            (features,) = features
            predictions = features.name

        xdata = []
        ydata = []

        async for record in sctx.with_features(
            list(mctx.np.hstack(mctx.features + [predictions]))
        ):
            feature_data = []
            predict_data = []
            for feature in record.features(mctx.features).values():
                feature_data.extend(
                    [feature] if mctx.np.isscalar(feature) else feature
                )
            xdata.append(feature_data)
            if is_multi:
                for feature in record.features(predictions).values():
                    predict_data.extend(
                        [feature] if mctx.np.isscalar(feature) else feature
                    )
            else:
                predict_data = record.feature(predictions)
            ydata.append(predict_data)
        xdata = mctx.np.array(xdata)
        ydata = mctx.np.array(ydata)
        mctx.logger.debug("Number of input records: {}".format(len(xdata)))
        mctx.confidence = mctx.parent.clf.score(xdata, ydata)
        return mctx.confidence


@entrypoint("skmodelscore")
class SklearnModelAccuracy(AccuracyScorer):
    CONFIG = SklearnModelAccuracyConfig
    CONTEXT = SklearnModelAccuracyContext
