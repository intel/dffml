import os
from typing import AsyncIterator, List

from dffml.base import config
from dffml.source.source import Sources
from dffml.util.entrypoint import entrypoint
from dffml.model import ModelNotTrained, ModelContext
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

    async def score(self, modelcontext: ModelContext, sources: Sources):
        if not os.path.isfile(
            os.path.join(modelcontext.model_dir_path, "saved_model.pb")
        ):
            raise ModelNotTrained("Train model before assessing for accuracy.")
        x, y = await modelcontext.train_data_generator(sources)
        accuracy_score = modelcontext._model.evaluate(x, y)
        return accuracy_score[1]


@entrypoint("textclf")
class TextClassifierAccuracy(AccuracyScorer):
    CONFIG = TextClassifierAccuracyConfig
    CONTEXT = TextClassifierAccuracyContext
