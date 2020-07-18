from typing import AsyncIterator, List

from dffml.base import config
from dffml.record import Record
from dffml.feature import Feature
from dffml.accuracy import AccuracyContext
from dffml.util.entrypoint import entrypoint


@config
class SimpleAccuracyConfig:
    pass


class SimpleAccuracyContext(AccuracyContext):
    def __init__(self, parent):
        super().__init__(parent)

    async def score(
        self,
        prediction_records: AsyncIterator[Record],
        prediction_feature: List[Feature],
    ):
        """
        Mean Squared Error
        """
        y = []
        y_predict = []
        async for record in prediction_records:
            y.append(record.features.prediction_feature)
            y_predict.append(record.predicttion.prediction_feature)
        accuracy = sum(
            list(map(lambda x, y: abs(x - y) ** 2, y, y_predict))
        ) / len(y)
        return accuracy


@entrypoint("simple_accuracy")
class SimpleAccuracy:
    CONFIG = SimpleAccuracyConfig
    CONTEXT = SimpleAccuracyContext
