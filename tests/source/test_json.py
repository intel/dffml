# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
from dffml.source.file import FileSourceConfig
from dffml.source.json import JSONSource
from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase


class TestCustomSQliteSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return JSONSource(FileSourceConfig(filename=self.testfile))
