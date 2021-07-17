from ..base import config
from ..record import Record
from ..feature import Feature
from ..model import ModelContext
from ..util.entrypoint import entrypoint
from ..source.source import SourcesContext
from .accuracy import (
    AccuracyScorer,
    AccuracyContext,
    InvalidNumberOfFeaturesError,
)


@config
class MeanSquaredErrorAccuracyConfig:
    pass


class MeanSquaredErrorAccuracyContext(AccuracyContext):
    """
    Mean Squared Error
    """

    async def score(self, mctx: ModelContext, sources: SourcesContext):
        if len([mctx.parent.config.predict]) != 1:
            raise InvalidNumberOfFeaturesError(
                f"{self.__class__.__qualname__} can only assess accuracy of one feature. features: {features}"
            )
        y = []
        y_predict = []
        async for record in mctx.predict(sources):
            y.append(record.feature(mctx.parent.config.predict.name))
            y_predict.append(
                record.prediction(mctx.parent.config.predict.name).value
            )
        accuracy = sum(
            list(map(lambda x, y: abs(x - y) ** 2, y, y_predict))
        ) / len(y)
        return accuracy


@entrypoint("mse")
class MeanSquaredErrorAccuracy(AccuracyScorer):
    CONFIG = MeanSquaredErrorAccuracyConfig
    CONTEXT = MeanSquaredErrorAccuracyContext
