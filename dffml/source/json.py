# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import json
import asyncio
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import Dict

from ..repo import Repo
from .memory import MemorySource
from .file import FileSource
from ..util.entrypoint import entry_point

from .log import LOGGER

LOGGER = LOGGER.getChild("json")


@dataclass
class OpenJSONFile:
    data: Dict[str, Dict]
    active: int
    lock: asyncio.Lock

    async def inc(self):
        async with self.lock:
            self.active += 1

    async def dec(self):
        async with self.lock:
            self.active -= 1
            return bool(self.active < 1)


@entry_point("json")
class JSONSource(FileSource, MemorySource):
    """
    JSONSource reads and write from a JSON file on open / close. Otherwise
    stored in memory.
    """

    OPEN_JSON_FILES: Dict[str, OpenJSONFile] = {}
    OPEN_JSON_FILES_LOCK: asyncio.Lock = asyncio.Lock()

    @asynccontextmanager
    async def _open_json(self, fd=None):
        async with self.OPEN_JSON_FILES_LOCK:
            if self.config.filename not in self.OPEN_JSON_FILES:
                self.logger.debug(f"{self.config.filename} first open")
                self.OPEN_JSON_FILES[self.config.filename] = OpenJSONFile(
                    data={}, active=1, lock=asyncio.Lock()
                )
                if fd is not None:
                    self.OPEN_JSON_FILES[
                        self.config.filename
                    ].data = json.load(fd)
            else:
                self.logger.debug(f"{self.config.filename} already open")
                await self.OPEN_JSON_FILES[self.config.filename].inc()
            yield

    async def _empty_file_init(self):
        async with self._open_json():
            return {}

    async def load_fd(self, fd):
        async with self._open_json(fd):
            repos = self.OPEN_JSON_FILES[self.config.filename].data
            self.mem = {
                src_url: Repo(src_url, data=data)
                for src_url, data in repos.get(self.config.label, {}).items()
            }
        LOGGER.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        async with self.OPEN_JSON_FILES_LOCK:
            repos = self.OPEN_JSON_FILES[self.config.filename].data
            repos[self.config.label] = {
                repo.src_url: repo.dict() for repo in self.mem.values()
            }
            self.logger.debug(f"{self.config.filename} updated")
            if await self.OPEN_JSON_FILES[self.config.filename].dec():
                del self.OPEN_JSON_FILES[self.config.filename]
                json.dump(repos, fd)
                self.logger.debug(f"{self.config.filename} written")
        LOGGER.debug("%r saved %d records", self, len(self.mem))
