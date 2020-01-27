# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Ports repos in JSON format
"""
import json

from .port import Port
from ..repo import Repo
from ..source.source import BaseSourceContext


class JSON(Port):
    """
    Imports and exports repos in JSON format
    """

    async def export_fd(self, sctx: BaseSourceContext, fd):
        json.dump({repo.key: repo.dict() async for repo in sctx.repos()}, fd)

    async def import_fd(self, sctx: BaseSourceContext, fd):
        for key, data in json.load(fd):
            await sctx.update(Repo(key, data=data))
