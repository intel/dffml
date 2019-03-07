# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Ports repos in JSON format
'''
import json

from .port import Port
from ..repo import Repo
from ..source import Source

class JSON(Port):
    '''
    Imports and exports repos in JSON format
    '''

    async def export_fd(self, source: Source, fd):
        json.dump({repo.src_url: repo.dict() async for repo in source.repos()},
                fd)

    async def import_fd(self, source: Source, fd):
        for src_url, data in json.load(fd):
            await source.update(Repo(src_url, data=data))
