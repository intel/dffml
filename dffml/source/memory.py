# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Fake data sources used for testing
"""
import asyncio
from typing import Any, Dict, List, NamedTuple, AsyncIterator

from ..base import BaseConfig
from ..repo import Repo
from .source import BaseSourceContext, BaseSource
from ..util.cli.arg import Arg
from ..util.entrypoint import entry_point


class MemorySourceContext(BaseSourceContext):
    async def update(self, repo):
        self.parent.mem[repo.src_url] = repo

    async def repos(self) -> AsyncIterator[Repo]:
        for repo in self.parent.mem.values():
            yield repo

    async def repo(self, src_url: str) -> Repo:
        return self.parent.mem.get(src_url, Repo(src_url))


class MemorySourceConfig(BaseConfig, NamedTuple):
    repos: List[Repo]


@entry_point("memory")
class MemorySource(BaseSource):
    """
    Stores repos in a dict in memory
    """

    CONTEXT = MemorySourceContext

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self.mem: Dict[str, Repo] = {}
        if isinstance(self.config, MemorySourceConfig):
            self.mem = {repo.src_url: repo for repo in self.config.repos}

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(
            args, above, "keys", Arg(type=str, nargs="+", default=[])
        )
        return args

    @classmethod
    def config(cls, config, *above):
        return MemorySourceConfig(
            repos=list(map(Repo, cls.config_get(config, above, "keys")))
        )
