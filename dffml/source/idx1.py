# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Loads records from an IDX1 file
"""
import struct

from ..record import Record
from ..base import config, field
from .memory import MemorySource
from .file import BinaryFileSource
from ..util.entrypoint import entrypoint


@config
class IDXSourceConfig:
    filename: str
    feature: str = field("Name of the feature the data will be referenced as")
    readwrite: bool = False
    allowempty: bool = False


class IDX1SourceConfig(IDXSourceConfig):
    pass


@entrypoint("idx1")
class IDX1Source(BinaryFileSource, MemorySource):
    """
    Source to read files in IDX1 format (such as MNIST digit label dataset).
    """

    CONFIG = IDX1SourceConfig

    async def load_fd(self, xfile):
        # Reading the binary datafile's details
        magic, size = struct.unpack(">II", xfile.read(8))

        # Reading the rest of binary datafile one byte at a time
        self.mem = {}
        for i in range(size):
            self.mem[str(i)] = Record(
                str(i),
                data={
                    "features": {
                        self.config.feature: struct.unpack(
                            ">b", xfile.read(1)
                        )[0]
                    }
                },
            )

        self.logger.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        raise NotImplementedError
