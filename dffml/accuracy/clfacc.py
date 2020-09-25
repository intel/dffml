from typing import AsyncIterator, List

from ..base import config
from ..record import Record
from ..feature import Feature
from ..util.entrypoint import entrypoint
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

    async def score(
        self, records: AsyncIterator[Record], features: List[Feature],
    ):
        if len(features) != 1:
            raise InvalidNumberOfFeaturesError(
                f"{self.__class__.__qualname__} can only assess accuracy of one feature. features: {features}"
            )
        total = 0
        right_predictions = 0
        async for record in records:
            if str(record.feature(features[0].name)) == str(
                record.prediction(features[0].name).value
            ):
                right_predictions += 1
            total += 1
        accuracy = right_predictions / total
        return accuracy


@entrypoint("clfacc")
class ClassificationAccuracy(AccuracyScorer):
    CONFIG = ClassificationAccuracyConfig
    CONTEXT = ClassificationAccuracyContext
