# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
WARNING: concurrent can be much slower for quick tasks. It is best used for long
running concurrent tasks.
'''
import random
import asyncio
from threading import Thread

from .log import LOGGER

class AsyncContextManagerList(list):

    def __init__(self, *args):
        super().__init__(list(args))

    async def __aenter__(self):
        for item in self:
            await item.__aenter__()
        # TODO Context management
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        for item in self:
            await item.__aexit__(exc_type, exc_value, traceback)
