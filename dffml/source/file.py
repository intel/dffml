# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import io
import abc
import bz2
import gzip
import lzma
import asyncio
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass, field, fields
from typing import NamedTuple, Tuple, Dict, List

from ..base import config
from .source import BaseSource
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..util.entrypoint import entry_point


@config
class FileSourceConfig:
    filename: str
    label: str = "unlabeled"
    readonly: bool = False


@entry_point("file")
class FileSource(BaseSource):
    """
    FileSource reads and write from a file on open / close.
    """

    CONFIG = FileSourceConfig

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
            self.logger.debug(
                ("%r is not a file, " % (self.config.filename,))
                + "initializing memory to empty dict"
            )
            self.mem = await self._empty_file_init()
            return
        if self.config.filename[::-1].startswith((".gz")[::-1]):
            opener = gzip.open(self.config.filename, "rt")
        elif self.config.filename[::-1].startswith((".bz2")[::-1]):
            opener = bz2.open(self.config.filename, "rt")
        elif self.config.filename[::-1].startswith(
            (".xz")[::-1]
        ) or self.config.filename[::-1].startswith((".lzma")[::-1]):
            opener = lzma.open(self.config.filename, "rt")
        elif self.config.filename[::-1].startswith((".zip")[::-1]):
            opener = self.zip_opener_helper()
        else:
            opener = open(self.config.filename, "r")
        with opener as fd:
            await self.load_fd(fd)

    async def _close(self):
        if not self.config.readonly:
            if self.config.filename[::-1].startswith((".gz")[::-1]):
                close = gzip.open(self.config.filename, "wt")
            elif self.config.filename[::-1].startswith((".bz2")[::-1]):
                close = bz2.open(self.config.filename, "wt")
            elif self.config.filename[::-1].startswith(
                (".xz")[::-1]
            ) or self.config.filename[::-1].startswith((".lzma")[::-1]):
                close = lzma.open(self.config.filename, "wt")
            elif self.config.filename[::-1].startswith((".zip")[::-1]):
                close = self.zip_closer_helper()
            else:
                close = open(self.config.filename, "w+")
            with close as fd:
                await self.dump_fd(fd)

    @contextmanager
    def zip_opener_helper(self):
        with zipfile.ZipFile(self.config.filename) as archive:
            with archive.open(self.__class__.__qualname__, mode="r") as zip_fd:
                with io.TextIOWrapper(zip_fd, write_through=True) as fd:
                    yield fd

    @contextmanager
    def zip_closer_helper(self):
        with zipfile.ZipFile(
            self.config.filename, "w", compression=zipfile.ZIP_BZIP2
        ) as archive:
            with archive.open(
                self.__class__.__qualname__, mode="w", force_zip64=True
            ) as zip_fd:
                with io.TextIOWrapper(zip_fd, write_through=True) as fd:
                    yield fd

    @abc.abstractmethod
    async def load_fd(self, fd):
        pass  # pragma: no cover

    @abc.abstractmethod
    async def dump_fd(self, fd):
        pass  # pragma: no cover
