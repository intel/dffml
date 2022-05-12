# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Feature subclasses are responsible for generating an integer value given an open
feature project's feature URL.
"""
import abc
import pydoc
import functools
import collections
from contextlib import AsyncExitStack
from typing import Any, List, Type

from .log import LOGGER
from ..util.data import parser_helper


class Hyperparameter(abc.ABC):
    """
    Class for all hyperparameters.

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

    LOGGER = LOGGER.getChild("Hyperparameter")

    ENTRYPOINT = "dffml.hyperparameter"

    def __init__(self, name: str) -> Any:
        super().__init__()
        if name.count(":") == 2:
            tempvar = name.split(":")
            name = tempvar[0]
            dtype = tempvar[1]
            vals = parser_helper(tempvar[2])
        if isinstance(dtype, str):
            dtype = self.convert_dtype(dtype)
        self.dtype = dtype
        self.vals = vals
        self.name = name

    def __eq__(self, other):
        if not all(
            map(functools.partial(hasattr, other), ["name", "dtype", "vals"])
        ):
            return False
        other_tuple = (other.name, other.dtype, other.vals)
        return bool(self_tuple == other_tuple)

    def __str__(self):
        return "%s(%s)" % (self.name, self.__class__.__qualname__)

    def __repr__(self):
        return "%s[%r, %r]" % (self.__str__(), self.dtype, self.vals)

    def export(self):
        return {
            "name": self.name,
            "dtype": self.dtype.__qualname__,
            "vals": self.vals,
        }

    @classmethod
    def _fromdict(cls, **kwargs):
        return Hyperparameter(**kwargs)

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


class Hyperparameters(collections.UserList):

    SINGLETON = Hyperparameter

    def __init__(self, *args: Hyperparameter) -> None:
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
                Hyperparameter._fromdict(**feature_data)
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
