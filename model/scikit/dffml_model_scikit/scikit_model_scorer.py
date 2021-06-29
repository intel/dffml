from dffml.base import config
from dffml.util.entrypoint import entrypoint
from dffml.source.source import SourcesContext
from dffml.model import ModelContext, ModelNotTrained
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

    async def score(self, mctx: ModelContext, sctx: SourcesContext):
        if not mctx._filepath.is_file():
            raise ModelNotTrained("Train model before assessing for accuracy.")

        if mctx.clf._estimator_type not in ("classifier", "regressor"):
            raise ScorerWillNotWork(
                "SklearnModelAccuracy will not work with Clustering Models"
            )

        xdata = []
        ydata = []

        async for record in sctx.with_features(
            mctx.features + [mctx.parent.config.predict.name]
        ):
            record_data = []
            for feature in record.features(mctx.features).values():
                record_data.extend(
                    [feature] if mctx.np.isscalar(feature) else feature
                )
            xdata.append(record_data)
            ydata.append(record.feature(mctx.parent.config.predict.name))
        xdata = mctx.np.array(xdata)
        ydata = mctx.np.array(ydata)
        mctx.logger.debug("Number of input records: {}".format(len(xdata)))
        mctx.confidence = mctx.clf.score(xdata, ydata)
        return mctx.confidence


@entrypoint("skmodelscore")
class SklearnModelAccuracy(AccuracyScorer):
    CONFIG = SklearnModelAccuracyConfig
    CONTEXT = SklearnModelAccuracyContext
