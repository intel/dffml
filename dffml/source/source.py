# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Source subclasses are responsible for generating an integer value given an open
source project's source URL.
'''
import abc
import asyncio
from typing import AsyncIterator, Dict, List, Optional, Callable

from .log import LOGGER
from ..repo import Repo, RepoData
from ..util.asynchelper import AsyncContextManagerList
from ..util.entrypoint import Entrypoint

class Source(abc.ABC, Entrypoint):
    '''
    Abstract base class for all sources. New sources must be derived from this
    class and implement the repos method.
    '''

    ENTRY_POINT = 'dffml.source'

    def __init__(self, src: str) -> None:
        self.src = src

    @abc.abstractmethod
    async def update(self, repo: Repo):
        '''
        Updates a repo for a source
        '''

    @abc.abstractmethod
    async def repos(self) -> AsyncIterator[Repo]:
        '''
        Returns a list of repos retrieved from self.src
        '''
        # mypy ignores AsyncIterator[Repo], therefore this is needed
        yield Repo('') # pragma: no cover

    @abc.abstractmethod
    async def repo(self, src_url: str):
        '''
        Get a repo from the source or add it if it doesn't exist
        '''

    @classmethod
    def load_from_dict(cls, sources: Dict[str, str]):
        '''
        Loads each source requested and instantiates it with its src_url.
        '''
        loaded: Dict[str, Source] = {}
        for src_url, name in sources.items():
            loaded[src_url] = cls.load(name)(src_url)
        return loaded

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__qualname__, self.src)

    async def open(self):
        return

    async def close(self):
        return

    async def __aenter__(self):
        await self.open()
        # TODO Context management
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

class Sources(AsyncContextManagerList):

    async def update(self, repo: Repo):
        '''
        Updates a repo for a source
        '''
        LOGGER.debug('Updating %r: %r', repo.src_url, repo.dict())
        for source in self:
            await source.update(repo)

    async def repos(self, validation: Optional[Callable[[Repo], bool]] = None) \
            -> AsyncIterator[Repo]:
        '''
        Retrieves repos from all sources
        '''
        for source in self:
            async for repo in source.repos():
                if validation is None or validation(repo):
                    yield repo

    async def repo(self, src_url: str):
        '''
        Retrieve and or register repo will all sources
        '''
        repo = Repo(src_url)
        for source in self:
            repo.merge(await source.repo(src_url))
        return repo

    async def classified_with_features(self,
            features: List[str]) -> AsyncIterator[Repo]:
        '''
        Returns all classified repos which have the requested features
        '''
        async for repo in self.repos(lambda repo: \
                bool(repo.features(features) and repo.classified())):
            yield repo

    async def unclassified_with_features(self,
            features: List[str]) -> AsyncIterator[Repo]:
        '''
        Returns all unclassified repos which have the requested features
        '''
        async for repo in self.repos(lambda repo: \
                bool(repo.features(features) and not repo.classified())):
            yield repo

    async def with_features(self, features: List[str]) -> AsyncIterator[Repo]:
        '''
        Returns all repos which have the requested features
        '''
        async for repo in self.repos(lambda repo: bool(repo.features(features))):
            yield repo

class SubsetSources(Sources):
    '''
    Restricts access to a subset of repos during iteration based on their keys.
    '''

    def __init__(self, *args: Source, keys: Optional[List[str]] = None) \
            -> None:
        super().__init__(*args)
        if keys is None:
            keys = []
        self.keys = keys

    async def repos(self, validation: Optional[Callable[[Repo], bool]] = None) \
            -> AsyncIterator[Repo]:
        for key in self.keys:
            repo = await self.repo(key)
            if validation is None or validation(repo):
                yield repo

class ValidationSources(Sources):
    '''
    Restricts access to a subset of repos during iteration based on a validation
    function.
    '''

    def __init__(self, *args: Source, validation: Callable[[Repo], bool]) \
            -> None:
        super().__init__(*args)
        self.validation = validation

    async def repos(self, validation: Optional[Callable[[Repo], bool]] = None) \
            -> AsyncIterator[Repo]:
        async for repo in super().repos():
            if self.validation(repo) \
                    and (validation is None or validation(repo)):
                yield repo
