import warnings
from typing import Union, Any

from ..base import config
from ..record import Record
from ..util.entrypoint import entrypoint
from .base import BaseSecretContext, BaseSecret
from ..source.memory import MemorySourceContext
from ..source.ini import INISourceConfig, INISource


@config
class INISecretConfig:
    filename: str
    readwrite: bool = True
    allowempty: bool = False


class INISecretContext(BaseSecretContext, MemorySourceContext):
    async def get(self, name: str) -> Union[None, str]:
        record = self.parent.mem.get("secrets", None)
        if not record:
            return None
        return record.features().get(name, None)

    async def set(self, name: str, value: Any):
        record = Record("secrets", data={"features": {name: value}})
        record.merge(self.parent.mem.get("secrets", Record("secrets")))
        await self.update(record)


@entrypoint("ini")
class INISecret(BaseSecret, INISource):

    CONTEXT = INISecretContext
    CONFIG = INISecretConfig

    def __init__(self, config: INISourceConfig):
        warnings.warn(
            """

            INSECURE This just writes secret to an ini file

            """
        )
        BaseSecret.__init__(self, config)
        INISource.__init__(self, config)
