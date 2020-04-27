# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Port subclasses import and export records.
"""
import abc

from ..source.source import BaseSource
from ..util.entrypoint import Entrypoint


class Port(abc.ABC, Entrypoint):
    """
    Port records into the format the porter understands
    """

    ENTRYPOINT = "dffml.port"

    @abc.abstractmethod
    async def export_fd(self, source: BaseSource, fd):
        """
        Export records
        """

    @abc.abstractmethod
    async def import_fd(self, source: BaseSource, fd):
        """
        Import records
        """

    async def export_to_file(self, source: BaseSource, filename: str):
        with open(filename, "w") as fd:
            await self.export_fd(source, fd)

    async def import_from_file(self, source: BaseSource, filename: str):
        with open(filename, "r") as fd:
            await self.import_fd(source, fd)
