from ..feature import Feature
from ..model import ModelContext
from ..util.entrypoint import entrypoint
from ..source.source import SourcesContext
from .accuracy import (
    AccuracyScorer,
    AccuracyContext,
)

from ..base import (
    config,
)


@config
class ClassificationAccuracyConfig:
    pass


class ClassificationAccuracyContext(AccuracyContext):
    """
    Classification Accuracy
    """

    async def score(
        self,
        mctx: ModelContext,
        sources: SourcesContext,
        feature: Feature,
    ):
        total = 0
        right_predictions = 0
        async for record in mctx.predict(sources):

            if str(record.feature(feature.name)) == str(
                int(record.prediction(feature.name).value)
            ):
                right_predictions += 1
            total += 1

        accuracy = right_predictions / total
        return accuracy


@entrypoint("clf")
class ClassificationAccuracy(AccuracyScorer):
    CONFIG = ClassificationAccuracyConfig
    CONTEXT = ClassificationAccuracyContext
