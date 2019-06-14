# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
from dffml.source.file import FileSourceConfig
from dffml.source.csv import CSVSource
from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase
from dffml.repo import Repo
import tempfile


class TestCSVSource(SourceTest, AsyncTestCase):
    async def setUpSource(self, fileobj):
        return CSVSource(FileSourceConfig(filename=fileobj.name))


class CSVTest(SourceTest, AsyncTestCase):
    async def setUpSource(self, fileobj):
        return CSVSource(FileSourceConfig(filename=fileobj.name))

    async def test_key(self):
        with tempfile.NamedTemporaryFile() as fileobj:
            fileobj.write(b"KeyHeader,ValueColumn\n")
            fileobj.write(b"a,42\n")
            fileobj.write(b"b,420\n")
            fileobj.seek(0)
            async with CSVSource(
                FileSourceConfig(filename=fileobj.name, key="KeyHeader")
            ) as source:
                async with source() as sctx:
                    repo_a = await sctx.repo("a")
                    repo_b = await sctx.repo("b")
                    self.assertEqual(repo_a.data.features["ValueColumn"], 42)
                    self.assertEqual(repo_b.data.features["ValueColumn"], 420)
