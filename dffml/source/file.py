# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import abc
import asyncio
import gzip
import bz2
import lzma
from .source import Source
from .log import LOGGER

LOGGER = LOGGER.getChild('file')

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
        if not os.path.exists(self.filename) \
                or os.path.isdir(self.filename):
            LOGGER.debug('%r is not a file, initializing memory to empty dict',
                         self.filename)
            self.mem = {}
            return
        if self.filename[::-1].startswith(('.gz')[::-1]):
            opener = gzip.open(self.filename, 'rt')
        elif self.filename[::-1].startswith(('.bz2')[::-1]):
            opener = bz2.open(self.filename, 'rt')
        elif self.filename[::-1].startswith(('.xz')[::-1]) or \
                self.filename[::-1].startswith(('.lzma')[::-1]):
            opener = lzma.open(self.filename, 'rt')
        else:
            opener = open(self.filename, 'r')
        with opener as fd:
            await self.load_fd(fd)

    async def close(self):
        await asyncio.shield(self._close())

    async def _close(self):
        if not self.readonly:
            if self.filename[::-1].startswith(('.gz')[::-1]):
                close = gzip.open(self.filename, 'wt')
            elif self.filename[::-1].startswith(('.bz2')[::-1]):
                close = bz2.open(self.filename, 'wt')
            elif self.filename[::-1].startswith(('.xz')[::-1]) or \
                    self.filename[::-1].startswith(('.lzma')[::-1]):
                close = lzma.open(self.filename, 'wt')
            else:
                close = open(self.filename, 'w')
            with close as fd:
                await self.dump_fd(fd)

    @abc.abstractmethod
    async def load_fd(self, fd):
        pass # pragma: no cover

    @abc.abstractmethod
    async def dump_fd(self, fd):
        pass # pragma: no cover
