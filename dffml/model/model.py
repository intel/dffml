# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Model subclasses are responsible for training themselves on repos, making
predictions about the classifications of repos, and assessing their prediction
accuracy.
'''
import abc
from typing import AsyncIterator, Tuple, Any, List, Optional

from ..repo import Repo
from ..source import Sources
from ..feature import Features
from ..accuracy import Accuracy
from ..util.entrypoint import Entrypoint

class Model(abc.ABC, Entrypoint):
    '''
    Abstract base class which should be derived from and implmented using
    various machine learning frameworks or concepts.
    '''

    ENTRY_POINT = 'dffml.model'

    def __init__(self, model_dir: Optional[str] = None) -> None:
        super().__init__()
        self.model_dir = model_dir

    @abc.abstractmethod
    async def train(self, sources: Sources, features: Features,
            classifications: List[Any], steps: int, num_epochs: int):
        '''
        Train using repos as the data to learn from.
        '''
        raise NotImplementedError()

    @abc.abstractmethod
    async def accuracy(self, sources: Sources, features: Features,
            classifications: List[Any]) -> Accuracy:
        '''
        Evaluates the accuracy of our model after training using the input repos
        as test data.
        '''
        raise NotImplementedError()

    @abc.abstractmethod
    async def predict(self, repos: AsyncIterator[Repo], features: Features,
            classifications: List[Any]) -> \
                    AsyncIterator[Tuple[Repo, Any, float]]:
        '''
        Uses trained data to make a prediction about the quality of a repo.
        '''
        raise NotImplementedError()
        yield (Repo(''), '', 0.0)

    @classmethod
    def installed(cls):
        return {key: model() for key, model in cls.load().items()}
