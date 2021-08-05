from typing import Union
from dffml.base import config
from dffml.util.entrypoint import entrypoint
from dffml.util.python import no_inplace_append
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
        self,
        mctx: ModelContext,
        predict_features: Union[Features, Feature],
        sctx: SourcesContext,
    ):
        if not mctx._filepath.is_file():
            raise ModelNotTrained("Train model before assessing for accuracy.")

        if mctx.clf._estimator_type not in ("classifier", "regressor"):
            raise ScorerWillNotWork(
                "SklearnModelAccuracy will not work with Clustering Models"
            )
        is_multi = isinstance(predict_features, Features)
        predictions = (
            predict_features.names() if is_multi else predict_features.name
        )

        xdata = []
        ydata = []

        async for record in sctx.with_features(
            list(mctx.np.hstack(no_inplace_append(mctx.features, predictions)))
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
        mctx.confidence = mctx.clf.score(xdata, ydata)
        return mctx.confidence


@entrypoint("skmodelscore")
class SklearnModelAccuracy(AccuracyScorer):
    CONFIG = SklearnModelAccuracyConfig
    CONTEXT = SklearnModelAccuracyContext
