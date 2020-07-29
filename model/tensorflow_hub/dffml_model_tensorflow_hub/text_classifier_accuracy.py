import os
from typing import AsyncIterator, List

from dffml.base import config
from dffml.record import Record
from dffml.feature import Feature
from dffml.model import ModelNotTrained
from dffml.util.entrypoint import entrypoint
from dffml.accuracy import (
    AccuracyScorer,
    AccuracyContext,
    InvalidNumberOfFeaturesError,
)


@config
class TextClassifierAccuracyConfig:
    pass


class TextClassifierAccuracyContext(AccuracyContext):
    """
    Evaluates the accuracy of our model after training using the input records
    as test data.
    """

    async def score(
        self, records: AsyncIterator[Record], features: List[Feature],
    ):
        if not os.path.isfile(
            os.path.join(self.model_dir_path, "saved_model.pb")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        x, y = await self.train_data_generator(records)
        accuracy_score = self._model.evaluate(x, y)
        return accuracy_score[1]


@entrypoint("textclassifieraccuracy")
class TextClassifierAccuracy(AccuracyScorer):
    CONFIG = TextClassifierAccuracyConfig
    CONTEXT = TextClassifierAccuracyContext
