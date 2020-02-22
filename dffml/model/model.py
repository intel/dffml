# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Model subclasses are responsible for training themselves on records, making
predictions about the value of a feature in the record, and assessing thei
prediction accuracy.
"""
import os
import abc
from typing import AsyncIterator

from ..base import (
    config,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from ..record import Record
from ..source.source import Sources
from ..feature import Features
from .accuracy import Accuracy
from ..util.entrypoint import base_entry_point


class ModelNotTrained(Exception):
    pass


@config
class ModelConfig:
    directory: str
    features: Features


class ModelContext(abc.ABC, BaseDataFlowFacilitatorObjectContext):
    """
    Abstract base class which should be derived from and implmented using
    various machine learning frameworks or concepts.
    """

    def __init__(self, parent: "Model") -> None:
        self.parent = parent

    @abc.abstractmethod
    async def train(self, sources: Sources):
        """
        Train using records as the data to learn from.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of our model after training using the input records
        as test data.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Record]:
        """
        Uses trained data to make a prediction about the quality of a record.
        """
        raise NotImplementedError()
        yield (Record(""), "", 0.0)  # skipcq: PYL-W0101


@base_entry_point("dffml.model", "model")
class Model(BaseDataFlowFacilitatorObject):
    """
    Abstract base class which should be derived from and implmented using
    various machine learning frameworks or concepts.
    """

    CONFIG = ModelConfig

    def __call__(self) -> ModelContext:
        # If the config object for this model contains the directory property
        # then create it if it does not exist
        directory = getattr(self.config, "directory", None)
        if directory is not None and not os.path.isdir(directory):
            os.makedirs(directory)
        return self.CONTEXT(self)
