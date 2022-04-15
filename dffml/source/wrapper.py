import inspect
import functools
import contextlib
import dataclasses
from typing import AsyncIterator

from ..record import Record
from ..util.entrypoint import entrypoint
from .source import BaseSource, BaseSourceContext, Sources
from ..util.config.inspect import make_config_inspect


class WrapperSourceContext(BaseSourceContext):
    async def update(self, record: Record):
        await self.sctx.update(record)

    async def record(self, key: str) -> AsyncIterator[Record]:
        return await self.sctx.record(key)

    async def records(self) -> AsyncIterator[Record]:
        async for record in self.sctx.records():
            yield record

    async def __aenter__(self) -> "WrapperSourceContext":
        self.sctx = await self.parent.source().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.sctx.__aexit__(exc_type, exc_value, traceback)


class WrapperSource(BaseSource):
    """
    Source used to wrap other sources

    Examples
    --------

    A memory source pre-populated with a some records.

    >>> from dffml.noasync import load
    >>> from dffml import (
    ...     BaseConfig,
    ...     WrapperSource,
    ...     MemorySource,
    ...     Record,
    ...     entrypoint,
    ... )
    >>>
    >>> @entrypoint("myrecords")
    ... class MyRecordsSource(WrapperSource):
    ...     CONFIG = BaseConfig
    ...
    ...     async def __aenter__(self) -> "MyRecordsSource":
    ...         self.source = MemorySource(records=[
    ...             Record("myrecord0", data={"features": {"a": 1}}),
    ...             Record("myrecord1", data={"features": {"b": 2}}),
    ...         ])
    ...         return await super().__aenter__()
    >>>
    >>> for record in load(MyRecordsSource()):
    ...     print(record.export())
    {'key': 'myrecord0', 'features': {'a': 1}, 'extra': {}}
    {'key': 'myrecord1', 'features': {'b': 2}, 'extra': {}}
    """

    CONTEXT = WrapperSourceContext

    async def __aenter__(self) -> "WrapperSource":
        await self.source.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.source.__aexit__(exc_type, exc_value, traceback)


class FunctionDidNotYieldSource(Exception):
    """
    Raised when the function wrapped by context_managed_wrapper_source() did not
    yield an object of instance :py:class:`dffml.source.source.BaseSource`.
    """


class FunctionMustBeGenerator(Exception):
    """
    Raised when the function to be wrapped by context_managed_wrapper_source()
    was not an async generator or a generator. The wrapped function must be one
    of the two in order to be made into a context manager.
    """


class ContextManagedWrapperSource(WrapperSource):
    async def __aenter__(self) -> "ContextManagedWrapperSource":
        # Handle async vs. non-async
        # TODO @config._asdict should NOT export, we should add a new .export()
        # method to @config which converts to primitive types. ._asdict() should
        # preseve typing information
        kwargs = dataclasses.asdict(self.config)
        if self.IS_ASYNC:
            async with self.WRAPPED(**kwargs) as source:
                pass
        else:
            with self.WRAPPED(**kwargs) as source:
                pass
        # Ensure the object returned really is a source
        if not isinstance(source, (BaseSource, Sources)):
            raise FunctionDidNotYieldSource(
                f"{self.WRAPPED} did not 'yield' an instantiated source. Instead it yielded {source!r}"
            )
        # Set the source property and aenter it via our parent class
        self.source = source
        return await super().__aenter__()

    @classmethod
    def remove_self_from_args(cls, args):
        """
        Remove class from args if called as method

        Examples
        --------

        >>> class MyConextManagedSource(ContextManagedWrapperSource):
        ...     def arg_zero_is_self_with_remove(*args):
        ...         args = MyConextManagedSource.remove_self_from_args(args)
        ...         return isinstance(args[0], MyConextManagedSource)
        ...
        ...     def arg_zero_is_self(*args):
        ...         return isinstance(args[0], MyConextManagedSource)
        >>>
        >>> source = MyConextManagedSource()
        >>> print(source.arg_zero_is_self("feedface"))
        True
        >>> print(source.arg_zero_is_self_with_remove("feedface"))
        False
        """
        args = list(args)
        if len(args) > 0 and isinstance(args[0], cls):
            args.pop(0)
        return args


def context_managed_wrapper_source(
    entrypoint_name, qualname_suffix: str = "Source"
) -> "ContextManagedWrapperSource":
    """
    Given a function which can function as a context manager (any function which
    uses the ``yield`` keyword). Make the function into a context manger or an
    async context manager depending on if it's defined ``async`` or not.

    Create a subclass of
    :py:class:`ContextManagedWrapperSource <dffml.source.wrapper.ContextManagedWrapperSource>`

    Examples
    --------

    A memory source pre-populated with a some records.

    >>> from dffml.noasync import load
    >>> from dffml import (
    ...     MemorySource,
    ...     Record,
    ...     context_managed_wrapper_source,
    ... )
    >>>
    >>> @context_managed_wrapper_source("my.records")
    ... def my_records():
    ...     yield MemorySource(records=[
    ...         Record("myrecord0", data={"features": {"a": 1}}),
    ...         Record("myrecord1", data={"features": {"b": 2}}),
    ...     ])
    >>>
    >>> print(my_records.source)
    <class 'dffml.base.MyRecordsSource'>
    >>> for record in load(my_records.source()):
    ...     print(record.export())
    {'key': 'myrecord0', 'features': {'a': 1}, 'extra': {}}
    {'key': 'myrecord1', 'features': {'b': 2}, 'extra': {}}
    >>>
    >>> @context_managed_wrapper_source("async.my.records")
    ... async def async_my_records():
    ...     yield MemorySource(records=[
    ...         Record("myrecord0", data={"features": {"a": 1}}),
    ...         Record("myrecord1", data={"features": {"b": 2}}),
    ...     ])
    >>>
    >>> print(async_my_records.source)
    <class 'dffml.base.AsyncMyRecordsSource'>
    >>> for record in load(async_my_records.source()):
    ...     print(record.export())
    {'key': 'myrecord0', 'features': {'a': 1}, 'extra': {}}
    {'key': 'myrecord1', 'features': {'b': 2}, 'extra': {}}
    """
    # Example: iris.training -> IrisTrainingDatasetSource
    class_name = (
        entrypoint_name.replace(".", " ").title().replace(" ", "")
        + qualname_suffix
    )

    def wrapper(func):
        # Handle async case. Func should be an async context manager if the
        # function was defined using `async def` rather than just `def`
        is_async = False
        if inspect.isasyncgenfunction(func):
            func = contextlib.asynccontextmanager(func)
            is_async = True

            @contextlib.asynccontextmanager
            async def wrapped(*args, **kwargs):
                async with func(
                    *ContextManagedWrapperSource.remove_self_from_args(args),
                    **kwargs,
                ) as source:
                    yield source

        elif inspect.isgeneratorfunction(func):
            func = contextlib.contextmanager(func)

            @contextlib.contextmanager
            def wrapped(*args, **kwargs):
                with func(
                    *ContextManagedWrapperSource.remove_self_from_args(args),
                    **kwargs,
                ) as source:
                    yield source

        else:
            raise FunctionMustBeGenerator(f"{func} does not 'yield'")

        # Wrap with functools
        wrapped = functools.wraps(func)(wrapped)

        # Create a new class whose name is the entry point name in camel case
        # with the suffix added. Whose parent class is
        # ContextManagedWrapperSource.
        # Create a new config class (@config) and set it as the CONFIG property
        # of the class we're creating. This will be used to configure the source
        # The properties of the config class will be taken from the arguments of
        # the function we are wrapping.
        # ContextManagedWrapperSource will call the WRAPPED function, which is
        # our func, and pass it the values of the properties of the config
        # class.
        # It will call it as an async context manager if IS_ASYNC is True.
        wrapped.source = entrypoint(entrypoint_name)(
            type(
                class_name,
                (ContextManagedWrapperSource,),
                {
                    "CONFIG": make_config_inspect(class_name + "Config", func),
                    "WRAPPED": wrapped,
                    "IS_ASYNC": is_async,
                },
            )
        )

        return wrapped

    return wrapper
