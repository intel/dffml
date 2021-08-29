from ..base import config
from ..feature import Feature
from ..model import ModelContext
from ..util.entrypoint import entrypoint
from ..source.source import SourcesContext
from .accuracy import (
    AccuracyScorer,
    AccuracyContext,
)


@config
class MeanSquaredErrorAccuracyConfig:
    pass


class MeanSquaredErrorAccuracyContext(AccuracyContext):
    """
    Mean Squared Error
    """

    async def score(
        self, mctx: ModelContext, sources: SourcesContext, feature: Feature,
    ):
        y = []
        y_predict = []
        async for record in mctx.predict(sources):
            y.append(record.feature(feature.name))
            y_predict.append(record.prediction(feature.name).value)
        accuracy = sum(
            list(map(lambda x, y: abs(x - y) ** 2, y, y_predict))
        ) / len(y)
        return accuracy


@entrypoint("mse")
class MeanSquaredErrorAccuracy(AccuracyScorer):
    CONFIG = MeanSquaredErrorAccuracyConfig
    CONTEXT = MeanSquaredErrorAccuracyContext
