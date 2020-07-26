# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Feature subclasses are responsible for generating an integer value given an open
feature project's feature URL.
"""
import abc
import pydoc
import asyncio
import functools
import collections
from contextlib import AsyncExitStack
from typing import List, Dict, Type, Any

from .log import LOGGER
from ..util.data import parser_helper
from ..util.entrypoint import Entrypoint


class Feature(abc.ABC):
    """
    Class for all features. 

    A feature is provided with the feature URL of the package (in self._key)
    and is expected to fetch any data it needs to calculate itself when fetch
    is called. All data fetched should be stored in tempdir() if it must reside
    on disk.

    Once the appropriate data is fetched the parse method is responsible for
    storing the parts of that data which will be used to calculate in the
    subclass

    Examples
    --------
    Define a feature:

    >>> from dffml import *
    >>>
    >>> feature = Feature("example", float, 10)
    >>> feature.dtype
    <class 'float'>
    >>> feature.name
    'example'
    >>> feature.length
    10

    """

    LOGGER = LOGGER.getChild("Feature")

    ENTRYPOINT = "dffml.feature"

    def __init__(self, name: str, dtype: Type = int, length: int = 1) -> Any:
        super().__init__()
        if name.count(":") == 2:
            tempvar = name.split(":")
            name = tempvar[0]
            dtype = tempvar[1]
            length = parser_helper(tempvar[2])
        if isinstance(dtype, str):
            dtype = self.convert_dtype(dtype)
        self.dtype = dtype
        self.length = length
        self.name = name

    def __eq__(self, other):
        if not all(
            map(functools.partial(hasattr, other), ["name", "dtype", "length"])
        ):
            return False
        self_tuple = (self.name, self.dtype, self.length)
        other_tuple = (other.name, other.dtype, other.length)
        return bool(self_tuple == other_tuple)

    def __str__(self):
        return "%s(%s)" % (self.name, self.__class__.__qualname__)

    def __repr__(self):
        return "%s[%r, %r]" % (self.__str__(), self.dtype, self.length)

    def export(self):
        return {
            "name": self.name,
            "dtype": self.dtype.__qualname__,
            "length": self.length,
        }

    @classmethod
    def _fromdict(cls, **kwargs):
        return Feature(**kwargs)

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


class Features(collections.UserList):

    SINGLETON = Feature

    def __init__(self, *args: Feature) -> None:
        super().__init__(args)
        self._stack = None

    def names(self) -> List[str]:
        return list(({feature.name: True for feature in self.data}).keys())

    def export(self):
        return {feature.name: feature.export() for feature in self.data}

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
        for item in self.data:
            await self._stack.enter_async_context(item)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._stack.aclose()
