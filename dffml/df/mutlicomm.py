import abc

from .base import (
    BaseDataFlowObjectContext,
    BaseDataFlowObject,
)
from ..util.entrypoint import base_entry_point

class BaseCommChannelConfig:
    """
    Config structure for a communication channel
    """

class BaseMultiCommContext(BaseDataFlowObjectContext, abc.ABC):
    """
    Abstract Base Class for mutlicomm contexts
    """

    def __init__(self, parent: "BaseMultiComm") -> None:
        self.parent = parent

    @abc.abstractmethod
    async def register(self, config: BaseCommChannelConfig) -> None:
        """
        Register a communication channel with the multicomm context.
        """


@base_entry_point("dffml.mutlicomm", "mc")
class BaseMultiComm(BaseDataFlowObject):
    """
    Abstract Base Class for mutlicomms
    """
