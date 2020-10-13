# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Fake data sources used for testing
"""
from typing import Dict, List, AsyncIterator

from ..base import config, field
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
    display: int = field(
        "When repr() is called, how many records to display", default=10
    )


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

    def __repr__(self):
        if isinstance(self.config, MemorySourceConfig):
            if not self.config.display:
                return "%s(%d records)" % (
                    self.__class__.__qualname__,
                    len(self.mem),
                )
            elif self.config.display == -1:
                return "%s(records=%r)" % (
                    self.__class__.__qualname__,
                    self.mem.values(),
                )
            elif len(self.mem) > self.config.display:
                first_n = [
                    record
                    for _, record in zip(
                        range(0, self.config.display), self.mem.values()
                    )
                ]
                return (
                    "%s(records=%r ... (only displaying %d records, %d total) ... )"
                    % (
                        self.__class__.__qualname__,
                        first_n,
                        self.config.display,
                        len(self.mem),
                    )
                )
        return super().__repr__()
