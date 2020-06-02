import abc
from typing import Union

from ..df.base import BaseDataFlowObjectContext, BaseDataFlowObject
from ..util.entrypoint import base_entry_point


class BaseSecretContext(BaseDataFlowObjectContext):
    def __init__(self, parent: "BaseSecret"):
        self.parent = parent

    @abc.abstractmethod
    async def get(self, name: str) -> Union[bytes, None]:
        """
        Get value mapped to name
        """

    @abc.abstractmethod
    async def set(self, name: str, value: bytes):
        """
        Store value and map it to name
        """


@base_entry_point("dffml.secret", "secret")
class BaseSecret(BaseDataFlowObject):
    """
    Base Class for secret storage
    """

    def __call__(self) -> BaseSecretContext:
        return self.CONTEXT(self)
