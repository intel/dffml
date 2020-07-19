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
class MeanSquaredErrorAccuracyConfig:
    pass


class MeanSquaredErrorAccuracyContext(AccuracyContext):
    """
    Mean Squared Error
    """

    async def score(
        self, records: AsyncIterator[Record], features: List[Feature],
    ):
        if len(features) != 1:
            raise InvalidNumberOfFeaturesError(
                f"{self.__class__.__qualname__} can only assess accuracy of one feature. features: {features}"
            )
        y = []
        y_predict = []
        async for record in records:
            y.append(record.feature(features[0].name))
            y_predict.append(record.prediction(features[0].name).value)
        accuracy = sum(
            list(map(lambda x, y: abs(x - y) ** 2, y, y_predict))
        ) / len(y)
        return accuracy


@entrypoint("mse")
class MeanSquaredErrorAccuracy(AccuracyScorer):
    CONFIG = MeanSquaredErrorAccuracyConfig
    CONTEXT = MeanSquaredErrorAccuracyContext
