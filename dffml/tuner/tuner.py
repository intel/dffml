import abc

from ..model import ModelContext
from ..source.source import SourcesContext
from ..accuracy.accuracy import AccuracyContext
from ..feature.feature import Feature
from ..util.entrypoint import base_entry_point
from ..base import (
    config,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)


@config
class TunerConfig:
    pass


class TunerContext(abc.ABC, BaseDataFlowFacilitatorObjectContext):
    def __init__(self, parent: "Tuner") -> None:
        self.parent = parent

    @abc.abstractmethod
    async def optimize(
        self,
        model: ModelContext,
        feature: Feature,
        accuracy_scorer: AccuracyContext,
        train_data: SourcesContext,
        test_data: SourcesContext,
    ) -> float:
        """
        Abstract method to optimize hyperparameters

        Parameters
        ----------
        model : ModelContext
            The Model which needs to be used.
        
        feature : Feature
            The Target feature in the data.

        accuracy_scorer: AccuracyContext
            The accuracy scorer that needs to be used.

        train_data: SourcesContext
            The train_data to train models on, with the hyperparameters provided.

        sources : SourcesContext
            The test_data to score against and optimize hyperparameters.

        Returns
        -------
        float
            The highest score value(optimized score)
        """
        raise NotImplementedError()


@base_entry_point("dffml.tuner", "tuner")
class Tuner(BaseDataFlowFacilitatorObject):
    """
    Abstract base class which should be derived from
    and implemented using various tuners.
    """

    CONFIG = TunerConfig
    CONTEXT = TunerContext

    def __call__(self) -> TunerContext:
        return self.CONTEXT(self)
