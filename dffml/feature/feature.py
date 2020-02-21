# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Feature subclasses are responsible for generating an integer value given an open
feature project's feature URL.
"""
import abc
import pydoc
import asyncio
from contextlib import AsyncExitStack
from typing import List, Dict, Type, Any

from .log import LOGGER
from ..util.monitor import Task
from ..util.entrypoint import Entrypoint


class Frequency(object):
    """
    Frequency in months
    """

    MONTHS: int = 0


class Quarterly(Frequency):
    """
    Evaluate on a quarterly basis (every 3 months).
    """

    MONTHS = 3


class Yearly(Frequency):
    """
    Evaluate on a yearly basis.
    """

    MONTHS = 12


class LoggingDict(object):
    def __init__(self, data: "Data") -> None:
        self.__data = data
        self.__dict: Dict = {}
        self.ignore = (asyncio.Lock,)

    async def get(self, key, default=None):
        val = self.__dict.get(key, default)
        return val

    async def set(self, key, value):
        self.__dict[key] = value
        if not isinstance(value, self.ignore):
            await self.__data.update({key: value}, event="set")

    async def inc(self, key, default=None, by=1):
        value = await self.get(key, default=default)
        value += by
        await self.set(key, value)
        return value


class Data(Task):
    """
    Passed to each feature during evaluation. Shared between all features a repo
    is being evaluated with
    """

    LOGGER = LOGGER.getChild("Data")

    def __init__(self, key: str) -> None:
        super().__init__(_key=key)
        self.key = key
        self.lock: asyncio.Lock = asyncio.Lock()
        self.temp: Dict[str, Any] = {}
        self.data: LoggingDict = LoggingDict(self)
        self.results: Dict[str, Any] = {}
        self.locks: Dict[str, Any] = {}

    async def mklock(self, name: str) -> asyncio.Lock:
        """
        Return a lock stored in data under the key `name`. Create the lock if it
        does not exist.
        """
        async with self.lock:
            lock = self.locks.get(name, None)
            if lock is None:
                lock = asyncio.Lock()
                self.locks[name] = lock
            return lock

    async def result(self):
        results = await self.complete()
        self.results = results
        self.LOGGER.debug("Data got results: %r", results)
        return results


class Feature(abc.ABC, Entrypoint):
    """
    Abstract base class for all features. New features must be derived from this
    class and implement the fetch, parse, and calc methods. These methods are
    always expected to be called in order. Anything you add to your feature
    subclass in fetch or parse is accessible in calc.

    A feature is provided with the feature URL of the package (in self._key)
    and is expected to fetch any data it needs to calculate itself when fetch
    is called. All data fetched should be stored in tempdir() if it must reside
    on disk.

    Once the appropriate data is fetched the parse method is responsible for
    storing the parts of that data which will be used to calculate in the
    subclass

    >>> self.__example_parsed_value_name = example_value

    The calc method then uses variables set in parse to output an integer value.

    >>>     def calc(self):
    >>>         return self.__example_parsed_value_name

    Full example of a feature implementation:

    >>> import glob
    >>> from dffml.feature import Feature
    >>>
    >>> class NumFilesFeature(Feature):
    >>>
    >>>     @abc.abstractmethod
    >>>     def fetch(self, data):
    >>>         self._downloader.vcs(self._key, self.tempdir('src'))
    >>>
    >>>     @abc.abstractmethod
    >>>     def parse(self, data):
    >>>         self.__num_files = glob.glob(self.tempdir(), recursive=True)
    >>>
    >>>     @abc.abstractmethod
    >>>     def calc(self, data):
    >>>         return self.__num_files
    """

    LOGGER = LOGGER.getChild("Feature")

    NAME: str = ""
    # LENGTH: int = 10
    # FREQUENCY: Type[Frequency] = Quarterly
    ENTRYPOINT = "dffml.feature"

    def __eq__(self, other):
        self_tuple = (self.NAME, self.dtype(), self.length())
        other_tuple = (other.NAME, other.dtype(), other.length())
        return bool(self_tuple == other_tuple)

    def __str__(self):
        return "%s(%s)" % (self.NAME, self.__class__.__qualname__)

    def __repr__(self):
        return "%s[%r, %d]" % (self.__str__(), self.dtype(), self.length())

    def export(self):
        return {
            "name": self.NAME,
            "dtype": self.dtype().__qualname__,
            "length": self.length(),
        }

    @classmethod
    def _fromdict(cls, **kwargs):
        return cls.load_def(**kwargs)

    def dtype(self) -> Type:
        """
        Models need to know a Feature's datatype.
        """
        self.LOGGER.warning("%s dtype unimplemented", self)
        return int

    def length(self) -> int:
        """
        Models need to know a Feature's length, 1 means single value, more than
        that is the length of the array calc returns.
        """
        self.LOGGER.warning("%s length unimplemented", self)
        return 1

    @classmethod
    def load(cls, loading=None):
        # CLI or dict compatibility
        # TODO Consolidate this
        if loading is not None:
            if isinstance(loading, dict):
                return cls.load_def(
                    loading["name"], loading["dtype"], loading["length"]
                )
            elif loading.count(":") == 2:
                return cls.load_def(*loading.split(":"))
        return super().load(loading)

    @classmethod
    def load_def(cls, name: str, dtype: str, length: str):
        return DefFeature(name, cls.convert_dtype(dtype), int(length))

    @classmethod
    def convert_dtype(cls, dtype: str):
        found = pydoc.locate(dtype)
        if found is None:
            raise TypeError("Failed to convert_dtype %r" % (dtype,))
        return found

    async def __aenter__(self):
        # TODO Context management
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass


def DefFeature(name, dtype, length):
    class DefinedFeature(Feature):

        LOGGER = LOGGER.getChild("DefFeature")

        def __init__(
            self, name: str = "", dtype: Type = int, length: int = 1
        ) -> None:
            super().__init__()
            self.NAME = name
            self._dtype = dtype
            self._length = length

        def dtype(self) -> Type:
            """
            Models need to know a Feature's datatype.
            """
            return self._dtype

        def length(self) -> int:
            """
            Models need to know a Feature's length, 1 means single value, more than
            that is the length of the array calc returns.
            """
            return self._length

    return DefinedFeature(name=name, dtype=dtype, length=length)


class Features(list):

    TIMEOUT: int = 60 * 2
    SINGLETON = Feature

    LOGGER = LOGGER.getChild("Features")

    def __init__(self, *args: Feature, timeout: int = None) -> None:
        super().__init__(args)
        self._stack = None
        self.timeout = timeout if not timeout is None else self.TIMEOUT

    def names(self) -> List[str]:
        return list(({feature.NAME: True for feature in self}).keys())

    def export(self):
        return {feature.NAME: feature.export() for feature in self}

    @classmethod
    def _fromdict(cls, **kwargs):
        for name, feature_def in kwargs.items():
            feature_def.setdefault("name", name)
        return cls(
            *[
                Feature._fromdict(**feature_data)
                for feature_data in kwargs.values()
            ]
        )

    async def __aenter__(self):
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        for item in self:
            await self._stack.enter_async_context(item)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._stack.aclose()
