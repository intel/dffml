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
class ClassificationAccuracyConfig:
    pass


class ClassificationAccuracyContext(AccuracyContext):
    """
    Classification Accuracy
    """

    async def score(self, mctx: ModelContext, sources: SourcesContext):
        if len([mctx.parent.config.predict]) != 1:
            raise InvalidNumberOfFeaturesError(
                f"{self.__class__.__qualname__} can only assess accuracy of one feature. features: {features}"
            )
        total = 0
        right_predictions = 0
        async for record in mctx.predict(sources):
            if str(record.feature(mctx.parent.config.predict.name)) == str(
                record.prediction(mctx.parent.config.predict.name).value
            ):
                right_predictions += 1
            total += 1
        accuracy = right_predictions / total
        return accuracy


@entrypoint("clf")
class ClassificationAccuracy(AccuracyScorer):
    CONFIG = ClassificationAccuracyConfig
    CONTEXT = ClassificationAccuracyContext
