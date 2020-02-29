# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Ports records in JSON format
"""
import json

from .port import Port
from ..record import Record
from ..source.source import BaseSourceContext


class JSON(Port):
    """
    Imports and exports records in JSON format
    """

    async def export_fd(self, sctx: BaseSourceContext, fd):
        json.dump(
            {record.key: record.dict() async for record in sctx.record()}, fd
        )

    async def import_fd(self, sctx: BaseSourceContext, fd):
        for key, data in json.load(fd):
            await sctx.update(Record(key, data=data))
