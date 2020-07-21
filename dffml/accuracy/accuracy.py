import abc
from typing import AsyncIterator, List

from ..record import Record
from ..feature import Feature
from ..util.entrypoint import base_entry_point
from ..base import (
    config,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)


class InvalidNumberOfFeaturesError(Exception):
    pass


@config
class AccuracyConfig:
    pass


class AccuracyContext(abc.ABC, BaseDataFlowFacilitatorObjectContext):
    def __init__(self, parent: "Accuracy") -> None:
        self.parent = parent

    @abc.abstractmethod
    async def score(
        self, records: AsyncIterator[Record], features: List[Feature],
    ) -> float:
        """
        Abstract method to get the score

        Parameters
        ----------
        records : AsyncIterator[Record]
            The predicted record, which we get by calling the predict method of a model

        features : List[Feature]
            The features on which the predtion was done

        Returns
        -------
        float
            The score value
        """
        raise NotImplementedError()


@base_entry_point("dffml.accuracy", "accuracy")
class AccuracyScorer(BaseDataFlowFacilitatorObject):
    """
    Abstract base class which should be derived from
    and implmented using various accuracy scorer.
    """

    CONFIG = AccuracyConfig
    CONTEXT = AccuracyContext

    def __call__(self) -> AccuracyContext:
        return self.CONTEXT(self)
