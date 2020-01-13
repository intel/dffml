# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
from dffml.source.json import JSONSource, JSONSourceConfig
from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase


class TestJSONSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return JSONSource(
            JSONSourceConfig(
                filename=self.testfile, allowempty=True, readwrite=True
            )
        )
