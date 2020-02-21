# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Fake data sources used for testing
"""
from typing import Dict, List, AsyncIterator

from ..base import config
from ..repo import Repo
from .source import BaseSourceContext, BaseSource
from ..util.entrypoint import entrypoint


class MemorySourceContext(BaseSourceContext):
    async def update(self, repo):
        self.parent.mem[repo.key] = repo

    async def repos(self) -> AsyncIterator[Repo]:
        for repo in self.parent.mem.values():
            yield repo

    async def repo(self, key: str) -> Repo:
        return self.parent.mem.get(key, Repo(key))


@config
class MemorySourceConfig:
    repos: List[Repo]


@entrypoint("memory")
class MemorySource(BaseSource):
    """
    Stores repos in a dict in memory
    """

    CONFIG = MemorySourceConfig
    CONTEXT = MemorySourceContext

    def __init__(self, config: MemorySourceConfig) -> None:
        super().__init__(config)
        self.mem: Dict[str, Repo] = {}
        if isinstance(self.config, MemorySourceConfig):
            self.mem = {repo.key: repo for repo in self.config.repos}
