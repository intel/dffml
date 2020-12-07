import abc

from ..model import ModelContext
from ..source.source import SourcesContext
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
        self, mctx: ModelContext, sources: SourcesContext,
    ) -> float:
        """
        Abstract method to get the score

        Parameters
        ----------
        mctx : ModelContext
            The Model which needs to be used.

        sources : SourcesContext
            The sources to use to get the accuracy

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
