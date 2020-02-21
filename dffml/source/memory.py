# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Fake data sources used for testing
"""
from typing import Dict, List, AsyncIterator

from ..base import config
from ..record import Record
from .source import BaseSourceContext, BaseSource
from ..util.entrypoint import entrypoint


class MemorySourceContext(BaseSourceContext):
    async def update(self, record):
        self.parent.mem[record.key] = record

    async def records(self) -> AsyncIterator[Record]:
        for record in self.parent.mem.values():
            yield record

    async def record(self, key: str) -> Record:
        return self.parent.mem.get(key, Record(key))


@config
class MemorySourceConfig:
    records: List[Record]


@entrypoint("memory")
class MemorySource(BaseSource):
    """
    Stores records in a dict in memory
    """

    CONFIG = MemorySourceConfig
    CONTEXT = MemorySourceContext

    def __init__(self, config: MemorySourceConfig) -> None:
        super().__init__(config)
        self.mem: Dict[str, Record] = {}
        if isinstance(self.config, MemorySourceConfig):
            self.mem = {record.key: record for record in self.config.records}
