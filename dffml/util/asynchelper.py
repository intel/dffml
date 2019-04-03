# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
WARNING: concurrent can be much slower for quick tasks. It is best used for long
running concurrent tasks.
'''
import asyncio
from contextlib import AsyncExitStack
from typing import Dict, Any, AsyncIterator, Tuple

from .log import LOGGER

class AsyncContextManagerList(list):

    def __init__(self, *args):
        super().__init__(list(args))
        self.__stack = None

    async def __aenter__(self):
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        for item in self:
            await self.__stack.enter_async_context(item)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__stack.aclose()

async def concurrently(work: Dict[asyncio.Task, Any],
                       *,
                       errors: str = 'strict') \
        -> AsyncIterator[Tuple[Any, Any]]:
    # Set up logger
    logger = LOGGER.getChild('concurrently')
    # Track if first run
    first = True
    # Set of tasks we are waiting on
    tasks = set(work.keys())
    # Return when outstanding operations reaches zero
    try:
        while first or tasks:
            first = False
            # Wait for incoming events
            done, _pending = await asyncio.wait(tasks,
                return_when=asyncio.FIRST_COMPLETED)

            for task in done:
                logger.debug('[%s] done', task)
                # Remove the task from the set of tasks we are waiting for
                tasks.remove(task)
                # Get the tasks exception if any
                exception = task.exception()
                if errors == 'strict' and exception is not None:
                    raise exception
                if exception is None:
                    yield work[task], task.result()
                else:
                    logger.debug('[%s] Ignoring exception: %s', task, exception)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
