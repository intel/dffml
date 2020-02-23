# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
from typing import AsyncIterator, Tuple, Any, List

from dffml.record import Record
from dffml.source.source import Sources
from dffml.feature import Features
from dffml.model.accuracy import Accuracy
from dffml.model.model import ModelContext, Model
from dffml.util.entrypoint import entrypoint
from dffml.base import config


@config
class MiscModelConfig:
    # This model never uses the directory, but chances are if you want to save
    # and load data from disk you will need to
    directory: str
    classifications: List[str]
    features: Features


class MiscModelContext(ModelContext):
    """
    Model wraping model_name API
    """

    async def train(self, sources: Sources):
        """
        Train using records as the data to learn from.
        """
        pass

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input records
        as test data.
        """
        # Lies
        return 1.0

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        """
        Uses trained data to make a prediction about the quality of a record.
        """
        async for record in records:
            yield record, self.parent.config.classifications[
                record.feature(self.parent.config.features.names()[0])
            ], 1.0


@entrypoint("misc")
class MiscModel(Model):

    CONTEXT = MiscModelContext
