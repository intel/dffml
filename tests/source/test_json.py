# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
from dffml.source import JSONSource
from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase

class TestJSONSource(SourceTest, AsyncTestCase):

    SOURCE = JSONSource

    async def setUpFile(self, fileobj):
        fileobj.write(b'{}')
        fileobj.seek(0)
