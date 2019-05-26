# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Source subclasses are responsible for generating an integer value given an open
source project's source URL.
"""
import abc
import asyncio
from typing import AsyncIterator, Dict, List, Optional, Callable, Tuple, Any

from ..base import (
    BaseConfig,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from ..repo import Repo, RepoData
from ..util.asynchelper import (
    AsyncContextManagerListContext,
    AsyncContextManagerList,
)
from ..util.entrypoint import Entrypoint

from .log import LOGGER


class BaseSourceContext(BaseDataFlowFacilitatorObjectContext):
    def __init__(self, parent: "BaseSource") -> None:
        self.parent = parent

    @abc.abstractmethod
    async def update(self, repo: Repo):
        """
        Updates a repo for a source
        """

    @abc.abstractmethod
    async def repos(self) -> AsyncIterator[Repo]:
        """
        Returns a list of repos retrieved from self.src
        """
        # mypy ignores AsyncIterator[Repo], therefore this is needed
        yield Repo("")  # pragma: no cover

    @abc.abstractmethod
    async def repo(self, src_url: str):
        """
        Get a repo from the source or add it if it doesn't exist
        """


class BaseSource(BaseDataFlowFacilitatorObject):
    """
    Abstract base class for all sources. New sources must be derived from this
    class and implement the repos method.
    """

    ENTRY_POINT = "dffml.source"
    ENTRY_POINT_NAME = ["source"]

    def __call__(self) -> BaseSourceContext:
        return self.CONTEXT(self)


class SourcesContext(AsyncContextManagerListContext):
    async def update(self, repo: Repo):
        """
        Updates a repo for a source
        """
        LOGGER.debug("Updating %r: %r", repo.src_url, repo.dict())
        for source in self:
            await source.update(repo)

    async def repos(
        self, validation: Optional[Callable[[Repo], bool]] = None
    ) -> AsyncIterator[Repo]:
        """
        Retrieves repos from all sources
        """
        for source in self:
            async for repo in source.repos():
                if validation is None or validation(repo):
                    yield repo

    async def repo(self, src_url: str):
        """
        Retrieve and or register repo will all sources
        """
        repo = Repo(src_url)
        for source in self:
            repo.merge(await source.repo(src_url))
        return repo

    async def classified_with_features(
        self, features: List[str]
    ) -> AsyncIterator[Repo]:
        """
        Returns all classified repos which have the requested features
        """
        async for repo in self.repos(
            lambda repo: bool(repo.features(features) and repo.classified())
        ):
            yield repo

    async def unclassified_with_features(
        self, features: List[str]
    ) -> AsyncIterator[Repo]:
        """
        Returns all unclassified repos which have the requested features
        """
        async for repo in self.repos(
            lambda repo: bool(
                repo.features(features) and not repo.classified()
            )
        ):
            yield repo

    async def with_features(self, features: List[str]) -> AsyncIterator[Repo]:
        """
        Returns all repos which have the requested features
        """
        async for repo in self.repos(
            lambda repo: bool(repo.features(features))
        ):
            yield repo


class Sources(AsyncContextManagerList):

    CONTEXT = SourcesContext


class ValidationSourcesContext(SourcesContext):
    async def repos(
        self, validation: Optional[Callable[[Repo], bool]] = None
    ) -> AsyncIterator[Repo]:
        async for repo in super().repos():
            if self.parent.validation(repo) and (
                validation is None or validation(repo)
            ):
                yield repo


class ValidationSources(Sources):
    """
    Restricts access to a subset of repos during iteration based on a validation
    function.
    """

    CONTEXT = ValidationSourcesContext

    def __init__(
        self, validation: Callable[[Repo], bool], *args: BaseSource
    ) -> None:
        super().__init__(*args)
        self.validation = validation


class SubsetSources(ValidationSources):
    """
    Restricts access to a subset of repos during iteration based on their keys.
    """

    def __init__(
        self, *args: BaseSource, keys: Optional[List[str]] = None
    ) -> None:
        super().__init__(self.__validation, *args)
        if keys is None:
            keys = []
        self.keys = keys

    def __validation(self, repo: Repo) -> bool:
        return bool(repo.src_url in self.keys)
