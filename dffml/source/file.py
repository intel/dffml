# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import io
import abc
import bz2
import gzip
import lzma
import errno
import zipfile
from contextlib import contextmanager

from ..base import config
from .source import BaseSource
from ..util.entrypoint import entrypoint


@config
class FileSourceConfig:
    filename: str
    tag: str = "untagged"
    readwrite: bool = False
    allowempty: bool = False


@entrypoint("file")
class FileSource(BaseSource):
    """
    FileSource reads and write from a file on open / close.
    """

    CONFIG = FileSourceConfig
    READMODE: str = "r"
    WRITEMODE: str = "w"
    READMODE_COMPRESSED: str = "rt"
    WRITEMODE_COMPRESSED: str = "wt"

    async def __aenter__(self) -> "BaseSourceContext":
        await self._open()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._close()

    async def _empty_file_init(self):
        return {}

    async def _open(self):
        if not os.path.exists(self.config.filename) or os.path.isdir(
            self.config.filename
        ):
            if self.config.allowempty:
                self.logger.debug(
                    ("%r is not a file, " % (self.config.filename,))
                    + "initializing memory to empty dict"
                )
                self.mem = await self._empty_file_init()
                return
            else:
                raise FileNotFoundError(
                    errno.ENOENT,
                    os.strerror(errno.ENOENT),
                    self.config.filename,
                )
        if self.config.filename[::-1].startswith((".gz")[::-1]):
            opener = gzip.open(self.config.filename, self.READMODE_COMPRESSED)
        elif self.config.filename[::-1].startswith((".bz2")[::-1]):
            opener = bz2.open(self.config.filename, self.READMODE_COMPRESSED)
        elif self.config.filename[::-1].startswith(
            (".xz")[::-1]
        ) or self.config.filename[::-1].startswith((".lzma")[::-1]):
            opener = lzma.open(self.config.filename, self.READMODE_COMPRESSED)
        elif self.config.filename[::-1].startswith((".zip")[::-1]):
            opener = self.zip_opener_helper()
        else:
            opener = open(self.config.filename, self.READMODE)
        with opener as fd:
            await self.load_fd(fd)

    async def _close(self):
        if self.config.readwrite:
            if self.config.filename[::-1].startswith((".gz")[::-1]):
                close = gzip.open(
                    self.config.filename, self.WRITEMODE_COMPRESSED
                )
            elif self.config.filename[::-1].startswith((".bz2")[::-1]):
                close = bz2.open(
                    self.config.filename, self.WRITEMODE_COMPRESSED
                )
            elif self.config.filename[::-1].startswith(
                (".xz")[::-1]
            ) or self.config.filename[::-1].startswith((".lzma")[::-1]):
                close = lzma.open(
                    self.config.filename, self.WRITEMODE_COMPRESSED
                )
            elif self.config.filename[::-1].startswith((".zip")[::-1]):
                close = self.zip_closer_helper()
            else:
                close = open(self.config.filename, "w+")
            with close as fd:
                await self.dump_fd(fd)

    @contextmanager
    def zip_opener_helper(self):
        with zipfile.ZipFile(self.config.filename) as archive:
            with archive.open(
                self.__class__.__qualname__, mode=self.READMODE
            ) as zip_fd:
                with io.TextIOWrapper(zip_fd, write_through=True) as fd:
                    yield fd

    @contextmanager
    def zip_closer_helper(self):
        with zipfile.ZipFile(
            self.config.filename, self.WRITEMODE, compression=zipfile.ZIP_BZIP2
        ) as archive:
            with archive.open(
                self.__class__.__qualname__,
                mode=self.WRITEMODE,
                force_zip64=True,
            ) as zip_fd:
                with io.TextIOWrapper(zip_fd, write_through=True) as fd:
                    yield fd

    @abc.abstractmethod
    async def load_fd(self, fd):
        pass  # pragma: no cover

    @abc.abstractmethod
    async def dump_fd(self, fd):
        pass  # pragma: no cover


@config
class BinaryFileSourceConfig(FileSourceConfig):
    pass


@entrypoint("binaryfile")
class BinaryFileSource(FileSource):
    CONFIG = BinaryFileSourceConfig
    READMODE: str = "rb"
    WRITEMODE: str = "wb"
    READMODE_COMPRESSED: str = "rb"
    WRITEMODE_COMPRESSED: str = "wb"
