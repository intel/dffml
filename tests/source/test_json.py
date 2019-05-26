# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
from dffml.source.file import FileSourceConfig
from dffml.source.json import JSONSource
from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase


class TestJSONSource(SourceTest, AsyncTestCase):

    SOURCE = JSONSource

    async def setUpFile(self, fileobj):
        fileobj.write(b"{}")
        fileobj.seek(0)

    async def setUpSource(self, fileobj):
        return JSONSource(FileSourceConfig(filename=fileobj.name))
