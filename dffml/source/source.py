# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Source subclasses are responsible for generating an integer value given an open
source project's source URL.
"""
import abc
from typing import AsyncIterator, List, Optional, Callable

from ..base import (
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from ..repo import Repo
from ..util.asynchelper import (
    AsyncContextManagerListContext,
    AsyncContextManagerList,
)

from ..util.entrypoint import base_entry_point
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
    async def repo(self, key: str):
        """
        Get a repo from the source or add it if it doesn't exist
        """


@base_entry_point("dffml.source", "source")
class BaseSource(BaseDataFlowFacilitatorObject):
    """
    Abstract base class for all sources. New sources must be derived from this
    class and implement the repos method.
    """

    def __call__(self) -> BaseSourceContext:
        return self.CONTEXT(self)


class SourcesContext(AsyncContextManagerListContext):
    async def update(self, repo: Repo):
        """
        Updates a repo for a source
        """
        LOGGER.debug("Updating %r: %r", repo.key, repo.dict())
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
                # NOTE In Python 3.7.3 self[1:] works, however in Python >
                # 3.7.3 only self.data works
                for other_source in self.data[1:]:
                    repo.merge(await other_source.repo(repo.key))
                if validation is None or validation(repo):
                    yield repo
            break

    async def repo(self, key: str):
        """
        Retrieve and or register repo will all sources
        """
        repo = Repo(key)
        for source in self:
            repo.merge(await source.repo(key))
        return repo

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
        return bool(repo.key in self.keys)
