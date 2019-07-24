# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import unittest
import tempfile

from dffml.source.file import FileSourceConfig
from dffml.source.csv import CSVSource, CSVSourceConfig
from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase
from dffml.repo import Repo
from dffml.util.cli.arg import parse_unknown


class TestCSVSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return CSVSource(CSVSourceConfig(filename=self.testfile))

    @unittest.skip("Labels not implemented yet for CSV files")
    async def test_label(self):
        """
        Labels not implemented yet for CSV files
        """

    def test_config_readonly_default(self):
        config = CSVSource.config(
            parse_unknown("--source-csv-filename", "feedface")
        )
        self.assertEqual(config.filename, "feedface")
        self.assertEqual(config.label, "unlabeled")
        self.assertEqual(config.key, None)
        self.assertFalse(config.readonly)

    def test_config_readonly_set(self):
        config = CSVSource.config(
            parse_unknown(
                "--source-csv-filename",
                "feedface",
                "--source-csv-label",
                "default-label",
                "--source-csv-key",
                "SourceURLColumn",
                "--source-csv-readonly",
            )
        )
        self.assertEqual(config.filename, "feedface")
        self.assertEqual(config.label, "default-label")
        self.assertEqual(config.key, "SourceURLColumn")
        self.assertTrue(config.readonly)

    async def test_key(self):
        with tempfile.NamedTemporaryFile() as fileobj:
            fileobj.write(b"KeyHeader,ValueColumn\n")
            fileobj.write(b"a,42\n")
            fileobj.write(b"b,420\n")
            fileobj.seek(0)
            async with CSVSource(
                CSVSourceConfig(filename=fileobj.name, key="KeyHeader")
            ) as source:
                async with source() as sctx:
                    repo_a = await sctx.repo("a")
                    repo_b = await sctx.repo("b")
                    self.assertEqual(repo_a.data.features["ValueColumn"], 42)
                    self.assertEqual(repo_b.data.features["ValueColumn"], 420)
