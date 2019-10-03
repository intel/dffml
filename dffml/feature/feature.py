# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Feature subclasses are responsible for generating an integer value given an open
feature project's feature URL.
"""
import abc
import pydoc
import asyncio
import traceback
import concurrent.futures as futures
import pkg_resources
from contextlib import AsyncExitStack
from functools import singledispatch, partial
from typing import Optional, List, Dict, Type, AsyncIterator, Any, Callable

from .log import LOGGER
from ..repo import Repo
from ..util.monitor import Monitor, Task
from ..util.entrypoint import Entrypoint
from ..util.asynchelper import AsyncContextManagerList


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

    def __init__(self, src_url: str) -> None:
        super().__init__(key=src_url)
        self.src_url = src_url
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

    A feature is provided with the feature URL of the package (in self._src_url)
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
    >>>         self._downloader.vcs(self._src_url, self.tempdir('src'))
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
    ENTRY_POINT = "dffml.feature"

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

    async def applicable(self, data) -> bool:
        return True

    async def fetch(self, data):
        """
        Fetch retrieves any additional information about the software we are
        evaluating. Any data fetched should be stored in tempdir().
        """
        pass

    async def parse(self, data):
        """
        Parse the data we downloaded in fetch() into a usable form.
        """
        pass

    async def calc(self, data):
        """
        Calculates the score for this feature based on data found by parse().
        """
        return False

    async def setUp(self, data):
        """
        Preform setup
        """
        pass

    async def tearDown(self, data, error=False):
        """
        Release any post calculation resources
        """
        pass

    async def open(self):
        """
        Opens any resources needed
        """
        pass

    async def close(self):
        """
        Closes any opened resources
        """
        pass

    @classmethod
    def load(cls, loading=None):
        if loading is not None and loading.startswith("def:"):
            return cls.load_def(*loading.replace("def:", "").split(":"))
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
        await self.open()
        # TODO Context management
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()


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


class Features(list, Monitor):

    TIMEOUT: int = 60 * 2

    LOGGER = LOGGER.getChild("Features")

    def __init__(self, *args: Feature, timeout: int = None) -> None:
        list.__init__(self, args)
        Monitor.__init__(self)
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

    async def evaluate(self, src: str, task: Task = None) -> Dict[str, Any]:
        return await asyncio.wait_for(
            self._evaluate(src, task=task), self.timeout
        )

    async def _evaluate(self, src: str, task: Task = None) -> Dict[str, Any]:
        """
        Evaluates all repos passed to it.
        Args:
            src: src of repo to be evaluated
            caching: If `True` sources will NOT be re-evaluated if they have
                     features
        Returns:
            A `dict` containing source URLs and their repos
        """
        toreDown = False
        data: Data = Data(src)
        if not task is None:
            data = task  # type: ignore
        features: Dict[str, Feature] = {}
        results: Dict[str, Any] = {}
        try:
            applicable = await self.applicable(data)
            self.LOGGER.debug("Applicable[%r]: %r", data.src_url, applicable)
            await applicable.on_all("setUp", data)
            await applicable.on_all("fetch", data)
            await applicable.on_all("parse", data)
            await applicable.run_calc(results, data)
            await applicable.on_all("tearDown", data)
            toreDown = True
        except futures._base.CancelledError as err:
            if not toreDown:
                await applicable.on_all("tearDown", data)
            return {}
        data.results.update(results)
        return results

    async def applicable(self, data: Data) -> "Features":
        return self.__class__(
            *[
                feature
                for feature in self
                if feature.NAME and await feature.applicable(data)
            ]
        )

    async def on_all(self, method_name: str, data: Data):
        await asyncio.gather(
            *[
                self.run_feature_method(
                    feature, getattr(feature, method_name), data
                )
                for feature in self
            ]
        )

    async def run_calc(self, results: Dict[str, Any], data: Data):
        await asyncio.gather(
            *[self._run_calc(feature, results, data) for feature in self]
        )

    async def _run_calc(
        self, feature: Feature, results: Dict[str, Any], data: Data
    ) -> Any:
        results[feature.NAME] = await self.run_feature_method(
            feature, feature.calc, data
        )

    async def run_feature_method(
        self, feature: Feature, method: Callable[[Data], Any], data: Data
    ) -> Any:
        error: Exception = Exception("Not an error")
        try:
            self.LOGGER.debug(
                "%s %s(%s).%s",
                data.src_url,
                feature.NAME,
                feature.__class__.__qualname__,
                method.__name__,
            )
            return await method(data)
        except futures._base.CancelledError as err:
            raise
        except Exception as err:
            error = err
            self.LOGGER.error(
                "Error evaluating %s: %s: %s",
                data.src_url,
                err,
                traceback.format_exc().strip(),
            )
        if str(error) != "Not an error":
            if method.__name__ != "tearDown":
                await feature.tearDown(data)
            self.remove(feature)

    def mktask(self, func, key):
        data = Data(key)
        Task.__init__(data, func, key)
        return data

    async def evaluate_repo(
        self, repo: Repo, *, features: List[str] = [], caching: bool = False
    ):
        results: Dict[str, Any] = repo.features(features)
        if caching and results:
            return repo
        try:
            results = await self.evaluate(repo.src_url)
            if results:
                repo.evaluated(results)
        except futures._base.TimeoutError:
            self.LOGGER.warning("Evaluation timed out: %s", repo.src_url)
        return repo

    async def evaluate_repos(
        self,
        repos: AsyncIterator[Repo],
        *,
        features: Optional[List[str]] = None,
        caching: bool = False,
        num_workers: int = 1,
    ):
        if features is None:
            features = self.names()
        sem = asyncio.Semaphore(value=num_workers)

        async def with_sem(sem, func, *args, **kwargs):
            async with sem:
                return await func(*args, **kwargs)

        evaluate_repo = partial(
            with_sem,
            sem,
            self.evaluate_repo,
            features=features,
            caching=caching,
        )
        for repo in await asyncio.gather(
            *[evaluate_repo(repo) async for repo in repos]
        ):
            yield repo

    async def submit(self, src: str):
        return await super().start(
            partial(self.evaluate, src), src, mktask=self.mktask
        )

    async def __aenter__(self):
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        for item in self:
            await self._stack.enter_async_context(item)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._stack.aclose()
