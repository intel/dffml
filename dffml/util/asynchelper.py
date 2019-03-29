# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
WARNING: concurrent can be much slower for quick tasks. It is best used for long
running concurrent tasks.
'''
from contextlib import AsyncExitStack

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
