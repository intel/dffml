# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Description of what this model does
'''
import abc
from typing import AsyncIterator, Tuple, Any, List, Optional

from dffml.repo import Repo
from dffml.source.source import Sources
from dffml.feature import Features
from dffml.accuracy import Accuracy
from dffml.model.model import ModelContext, Model
from dffml.util.entrypoint import entry_point

class MiscContext(ModelContext):
    '''
    Model wraping model_name API
    '''

    async def train(self, sources: Sources, features: Features,
            classifications: List[Any]):
        '''
        Train using repos as the data to learn from.
        '''
        pass

    async def accuracy(self, sources: Sources, features: Features,
            classifications: List[Any]) -> Accuracy:
        '''
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        '''
        # Lies
        return 1.0

    async def predict(self, repos: AsyncIterator[Repo], features: Features,
            classifications: List[Any]) -> \
                    AsyncIterator[Tuple[Repo, Any, float]]:
        '''
        Uses trained data to make a prediction about the quality of a repo.
        '''
        async for repo in repos:
            yield repo, classifications[0], 1.0

@entry_point('misc')
class Misc(Model):

    CONTEXT = MiscContext
