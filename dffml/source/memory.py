# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Fake data sources used for testing
'''
import asyncio
from typing import Dict, AsyncIterator

from ..repo import Repo
from .source import Source

class MemorySource(Source):
    '''
    Stores repos in a dict in memory
    '''

    def __init__(self, src: str) -> None:
        super().__init__(src)
        self.mem: Dict[str, Repo] = {}
        self.lock = asyncio.Lock()

    async def update(self, repo):
        async with self.lock:
            self.mem[repo.src_url] = repo

    async def repos(self) -> AsyncIterator[Repo]:
        # NOTE No lock used here because sometimes we iterate and update
        # Feel free to debate this by opening an issue.
        for repo in self.mem.values():
            yield repo

    async def repo(self, src_url: str) -> Repo:
        async with self.lock:
            return self.mem.get(src_url, Repo(src_url))

class RepoSource(MemorySource):
    '''
    Takes repo data from instantiation arguments. Stores repos in memory.
    '''

    def __init__(self, *args: Repo, src: str = '') -> None:
        super().__init__(src)
        self.mem = {repo.src_url: repo for repo in args}
