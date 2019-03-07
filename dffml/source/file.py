# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import abc
import asyncio

from .source import Source
# from .log import LOGGER

# LOGGER = LOGGER.getChild('file')

class FileSource(Source):
    '''
    FileSource reads and write from a file on open / close.
    '''

    @property
    def readonly(self) -> bool:
        return bool(self.src[::-1].startswith((':ro')[::-1]))

    @property
    def filename(self):
        '''
        Path to JSON file used for storage on disk.
        '''
        if self.readonly:
            return self.src[:-3]
        return self.src

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__qualname__, self.filename)

    async def open(self):
        await asyncio.shield(self._open())

    async def _open(self):
        if not os.path.isfile(self.filename):
            self.mem = {}
            return
        with open(self.filename, 'r') as fd:
            await self.load_fd(fd)

    async def close(self):
        await asyncio.shield(self._close())

    async def _close(self):
        if not self.readonly:
            with open(self.filename, 'w') as fd:
                await self.dump_fd(fd)

    @abc.abstractmethod
    async def load_fd(self, fd):
        pass # pragma: no cover

    @abc.abstractmethod
    async def dump_fd(self, fd):
        pass # pragma: no cover
