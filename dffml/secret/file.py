import os
import hashlib
import asyncio
import pathlib
from typing import Union,Any

from ..base import config
from ..util.entrypoint import entrypoint
from .base import BaseSecretContext, BaseSecret

from dffml.high_level import Record
from ..source.memory import MemorySourceContext
from ..source.ini import INISourceConfig,INISource



class FileSecretContext(BaseSecretContext, MemorySourceContext):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)


    async def get(self, name: str) -> Union[None, str]:
        with open(self.parent.config.filename,'r+') as fd:
            await self.parent.load_fd(fd)
        record = self.parent.mem.get(name,None)
        if not record:
            return None
        return record.feature('data')

    async def set(self, name: str, value: Any):
        record = Record(name, data={"features": {"data": value}})
        await self.update(record)
        with open(self.parent.config.filename,'w+') as fd:
            await self.parent.dump_fd(fd)



@entrypoint("file")
class FileSecret(BaseSecret,INISource):

    CONTEXT = FileSecretContext
    CONFIG = INISourceConfig

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.mem: Dict[str, Record] = {}