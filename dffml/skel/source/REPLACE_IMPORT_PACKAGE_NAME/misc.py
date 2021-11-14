from typing import AsyncIterator, Dict, List

from dffml.base import BaseConfig
from dffml.record import Record
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entrypoint
from dffml.base import config


@config
class MiscSourceConfig:
    records: List[Record]


class MiscSourceContext(BaseSourceContext):
    async def update(self, record):
        self.parent.mem[record.key] = record

    async def records(self) -> AsyncIterator[Record]:
        for record in self.parent.mem.values():
            yield record

    async def record(self, key: str) -> Record:
        return self.parent.mem.get(key, Record(key))


@entrypoint("misc")
class MiscSource(BaseSource):
    """
    Stores records ... somewhere! (skeleton template is in memory)
    """

    CONTEXT = MiscSourceContext

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self.mem: Dict[str, Record] = {}
        if isinstance(self.config, MiscSourceConfig):
            self.mem = {record.key: record for record in self.config.records}
