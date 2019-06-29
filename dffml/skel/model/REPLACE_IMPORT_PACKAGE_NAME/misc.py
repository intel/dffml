# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Description of what this model does
"""
import abc
from typing import AsyncIterator, Tuple, Any, List, Optional, NamedTuple

from dffml.repo import Repo
from dffml.source.source import Sources
from dffml.feature import Features
from dffml.accuracy import Accuracy
from dffml.model.model import ModelConfig, ModelContext, Model
from dffml.util.entrypoint import entry_point


class MiscModelConfig(ModelConfig, NamedTuple):
    # This model never uses the directory, but chances are if you want to save
    # and load data from disk you will need to
    directory: str
    classifications: List[str]


class MiscModelContext(ModelContext):
    """
    Model wraping model_name API
    """

    async def train(self, sources: Sources):
        """
        Train using repos as the data to learn from.
        """
        pass

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        """
        # Lies
        return 1.0

    async def predict(
        self, repos: AsyncIterator[Repo]
    ) -> AsyncIterator[Tuple[Repo, Any, float]]:
        """
        Uses trained data to make a prediction about the quality of a repo.
        """
        async for repo in repos:
            yield repo, self.parent.config.classifications[
                repo.feature(self.features.names()[0])
            ], 1.0


@entry_point("misc")
class MiscModel(Model):

    CONTEXT = MiscModelContext
