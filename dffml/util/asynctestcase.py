# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Adds support for test cases which need to be run in an event loop.
"""
import os
import random
import pathlib
import asyncio
import inspect
import logging
import unittest
import tempfile
import contextlib
from typing import Optional


class AsyncTestCase(unittest.TestCase):
    """
    Runs any test_ methods as coroutines in the default event loop.

    USAGE
    >>> from dffml.util.asynctestcase import AsyncTestCase
    >>>
    >>> class AsyncTestCase(unittest.AsyncTestCase):
    >>>
    >>>     async def test_sleep(self):
    >>>         await asyncio.sleep(1)
    """

    # The event loop to run test_ functions in
    loop = asyncio.get_event_loop()

    def async_wrapper(self, coro):
        """
        Returns a function which calls the test_ function which calls
        loop.run_until_complete to return the result of the test.
        """

        def run_it(*args, **kwargs):
            """
            Calls the loop's run_until_complete method.
            """
            logging.basicConfig(
                level=getattr(
                    logging,
                    os.getenv("LOGGING", "CRITICAL").upper(),
                    logging.CRITICAL,
                )
            )
            result = self.loop.run_until_complete(coro(*args, **kwargs))
            logging.basicConfig(level=logging.CRITICAL)
            return result

        return run_it

    def run(self, result=None):
        """
        Convert all test_ methods via async_wrapper so that they are run in the
        event loop.
        """
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for name, method in methods:
            if inspect.iscoroutinefunction(method) and (
                name.startswith("test_") or name in ["setUp", "tearDown"]
            ):
                setattr(self, name, self.async_wrapper(method))
        return super().run(result=result)


@contextlib.contextmanager
def non_existant_tempfile():
    """
    Yield the filename of a non-existant file within a temporary directory
    """
    with tempfile.TemporaryDirectory() as testdir:
        yield os.path.join(testdir, str(random.random()))


class AsyncExitStackTestCase(AsyncTestCase):
    async def setUp(self):
        super().setUp()
        self._stack = contextlib.ExitStack().__enter__()
        self._astack = await contextlib.AsyncExitStack().__aenter__()

    async def tearDown(self):
        super().tearDown()
        self._stack.__exit__(None, None, None)
        await self._astack.__aexit__(None, None, None)

    def mktempfile(
        self, suffix: Optional[str] = None, text: Optional[str] = None
    ):
        filename = self._stack.enter_context(non_existant_tempfile())
        if suffix:
            filename = filename + suffix
        if text:
            pathlib.Path(filename).write_text(inspect.cleandoc(text) + "\n")
        return filename
