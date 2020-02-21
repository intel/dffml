# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Loads records from an IDX3 file
"""
import struct

from ..record import Record
from ..util.entrypoint import entrypoint
from .idx1 import IDX1Source, IDXSourceConfig


class IDX3SourceConfig(IDXSourceConfig):
    pass


@entrypoint("idx3")
class IDX3Source(IDX1Source):
    """
    Source to read files in IDX3 format (such as MNIST digit image dataset).
    """

    CONFIG = IDX3SourceConfig

    async def load_fd(self, xfile):
        # Reading the binary datafile's details
        magic, size = struct.unpack(">II", xfile.read(8))
        nrows, ncols = struct.unpack(">II", xfile.read(8))

        self.mem = {}
        inner_array_size = nrows * ncols
        for i in range(0, size):
            self.mem[str(i)] = Record(
                str(i),
                data={
                    "features": {
                        self.config.feature: struct.unpack(
                            f">{inner_array_size}B",
                            xfile.read(inner_array_size),
                        )
                    }
                },
            )

        self.logger.debug("%r loaded %d records", self, len(self.mem))
