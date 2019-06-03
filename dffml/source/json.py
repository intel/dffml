# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import json

from ..repo import Repo
from .memory import MemorySource
from .file import FileSource

from .log import LOGGER

LOGGER = LOGGER.getChild("json")


class JSONSource(FileSource, MemorySource):
    """
    JSONSource reads and write from a JSON file on open / close. Otherwise
    stored in memory.
    """

    def __init__(self, config):
        super().__init__(config)
        self.repos = {}

    async def load_fd(self, fd):
        self.repos = json.load(fd)
        self.mem = {
            src_url: Repo(src_url, data=data)
            for src_url, data in self.repos.get(self.config.label, {}).items()
        }
        LOGGER.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        self.repos[self.config.label] = {
            repo.src_url: repo.dict() for repo in self.mem.values()
        }
        json.dump(self.repos, fd)
        LOGGER.debug("%r saved %d records", self, len(self.mem))
