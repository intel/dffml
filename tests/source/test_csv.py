# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
from dffml.source.file import FileSourceConfig
from dffml.source.csv import CSVSource
from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase


class TestCSVSource(SourceTest, AsyncTestCase):
    async def setUpSource(self, fileobj):
        return CSVSource(FileSourceConfig(filename=fileobj.name))
