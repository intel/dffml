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
from ..record import Record
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
    async def update(self, record: Record):
        """
        Updates a record for a source

        Examples
        --------
        >>> async def main():
        ...     async with MemorySource(records=[]) as source:
        ...         # Open, update, and close
        ...         async with source() as ctx:
        ...             example = Record("one", data=dict(features=dict(feed="face")))
        ...             # ... Update one into our records ...
        ...             await ctx.update(example)
        ...             # Let's check out our records after calling `record` and `update`.
        ...             async for record in ctx.records():
        ...                 print(record.export())
        >>>
        >>> asyncio.run(main())
        {'key': 'one', 'features': {'feed': 'face'}, 'extra': {}}
        """

    @abc.abstractmethod
    async def records(self) -> AsyncIterator[Record]:
        """
        Returns a list of records retrieved from self.src

        Examples
        --------
        >>> async def main():
        ...     async with MemorySource(records=[Record("example", data=dict(features=dict(dead="beef")))]) as source:
        ...         async with source() as ctx:
        ...             async for record in ctx.records():
        ...                 print(record.export())
        >>>
        >>> asyncio.run(main())
        {'key': 'example', 'features': {'dead': 'beef'}, 'extra': {}}
        """
        # mypy ignores AsyncIterator[Record], therefore this is needed
        yield Record("")  # pragma: no cover

    @abc.abstractmethod
    async def record(self, key: str):
        """
        Get a record from the source or add it if it doesn't exist.

        Examples
        --------
        >>> async def main():
        ...     async with MemorySource(records=[Record("example", data=dict(features=dict(dead="beef")))]) as source:
        ...         # Open, update, and close
        ...         async with source() as ctx:
        ...             example = await ctx.record("example")
        ...             # Let's also try calling `record` for a record that doesnt exist.
        ...             one = await ctx.record("one")
        ...             await ctx.update(one)
        ...             async for record in ctx.records():
        ...                 print(record.export())
        >>>
        >>> asyncio.run(main())
        {'key': 'example', 'features': {'dead': 'beef'}, 'extra': {}}
        {'key': 'one', 'extra': {}}
        """


@base_entry_point("dffml.source", "source")
class BaseSource(BaseDataFlowFacilitatorObject):
    """
    Abstract base class for all sources. New sources must be derived from this
    class and implement the records method.
    """

    def __call__(self) -> BaseSourceContext:
        return self.CONTEXT(self)


class SourcesContext(AsyncContextManagerListContext):
    async def update(self, record: Record):
        """
        Updates a record for a source
        """
        LOGGER.debug("Updating %r: %r", record.key, record.dict())
        for source in self:
            await source.update(record)

    async def records(
        self, validation: Optional[Callable[[Record], bool]] = None
    ) -> AsyncIterator[Record]:
        """
        Retrieves records from all sources
        """
        for source in self:
            async for record in source.records():
                # NOTE In Python 3.7.3 self[1:] works, however in Python >
                # 3.7.3 only self.data works
                for other_source in self.data[1:]:
                    record.merge(await other_source.record(record.key))
                if validation is None or validation(record):
                    yield record
            break

    async def record(self, key: str):
        """
        Retrieve and or register record will all sources
        """
        record = Record(key)
        for source in self:
            record.merge(await source.record(key))
        return record

    async def with_features(
        self, features: List[str]
    ) -> AsyncIterator[Record]:
        """
        Returns all records which have the requested features
        """
        async for record in self.records(
            lambda record: bool(record.features(features))
        ):
            yield record


class Sources(AsyncContextManagerList):

    CONTEXT = SourcesContext


class ValidationSourcesContext(SourcesContext):
    async def records(
        self, validation: Optional[Callable[[Record], bool]] = None
    ) -> AsyncIterator[Record]:
        async for record in super().records():
            if self.parent.validation(record) and (
                validation is None or validation(record)
            ):
                yield record


class ValidationSources(Sources):
    """
    Restricts access to a subset of records during iteration based on a validation
    function.
    """

    CONTEXT = ValidationSourcesContext

    def __init__(
        self, validation: Callable[[Record], bool], *args: BaseSource
    ) -> None:
        super().__init__(*args)
        self.validation = validation


class SubsetSources(ValidationSources):
    """
    Restricts access to a subset of records during iteration based on their keys.
    """

    def __init__(
        self, *args: BaseSource, keys: Optional[List[str]] = None
    ) -> None:
        super().__init__(self.__validation, *args)
        if keys is None:
            keys = []
        self.keys = keys

    def __validation(self, record: Record) -> bool:
        return bool(record.key in self.keys)
