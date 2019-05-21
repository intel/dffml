# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Model subclasses are responsible for training themselves on repos, making
predictions about the classifications of repos, and assessing their prediction
accuracy.
'''
import os
import abc
from typing import AsyncIterator, Tuple, Any, List, Optional, NamedTuple, Dict

from ..base import BaseConfig, \
                   BaseDataFlowFacilitatorObjectContext, \
                   BaseDataFlowFacilitatorObject
from ..util.cli.arg import Arg
from ..repo import Repo
from ..source.source import Sources
from ..feature import Features
from ..accuracy import Accuracy
from ..util.entrypoint import Entrypoint, base_entry_point

class ModelConfig(BaseConfig, NamedTuple):
    directory: str

class ModelContext(abc.ABC, BaseDataFlowFacilitatorObjectContext):
    '''
    Abstract base class which should be derived from and implmented using
    various machine learning frameworks or concepts.
    '''

    def __init__(self, parent: 'Model') -> None:
        self.parent = parent

    @abc.abstractmethod
    async def train(self, sources: Sources, features: Features,
            classifications: List[Any]):
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

@base_entry_point('dffml.model', 'model')
class Model(BaseDataFlowFacilitatorObject):
    '''
    Abstract base class which should be derived from and implmented using
    various machine learning frameworks or concepts.
    '''

    def __call__(self) -> ModelContext:
        # If the config object for this model contains the directory property
        # then create it if it does not exist
        directory = getattr(self.config, 'directory', None)
        if directory is not None and not os.path.isdir(directory):
            os.makedirs(directory)
        return self.CONTEXT(self)

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, 'directory', Arg(
            default=os.path.join(os.path.expanduser('~'), '.cache', 'dffml')))
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return ModelConfig(
            directory=cls.config_get(config, above, 'directory')
        )
