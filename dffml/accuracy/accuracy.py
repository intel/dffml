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


@config
class AccuracyConfig:
    pass


class AccuracyContext(abc.ABC, BaseDataFlowFacilitatorObjectContext):
    def __init__(self, parent: "Accuracy") -> None:
        self.parent = parent

    @abc.abstractmethod
    async def score(
        self,
        prediction_records: AsyncIterator[Record],
        prediction_feature: List[Feature],
    ) -> float:
        """
        Abstract method to get the score

        Parameters
        ----------
        prediction : AsyncIterator[Record]
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
    and implmented using various machine learning
    frameworks or concepts.
    """

    CONFIG = AccuracyConfig
    CONTEXT = AccuracyContext
