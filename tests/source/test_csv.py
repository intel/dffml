# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import tempfile
import os
import csv
import random
import pathlib
import inspect

from dffml.source.csv import CSVSource, CSVSourceConfig
from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase
from dffml.record import Record
from dffml.util.cli.arg import parse_unknown


class TestCSVSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return CSVSource(
            CSVSourceConfig(
                filename=self.testfile, allowempty=True, readwrite=True
            )
        )

    async def test_tag(self):
        with tempfile.TemporaryDirectory() as testdir:
            self.testfile = os.path.join(testdir, str(random.random()))
            untagged = await self.setUpSource()
            tagged = await self.setUpSource()
            tagged.config = tagged.config._replace(tag="sometag")
            async with untagged, tagged:
                async with untagged() as uctx, tagged() as lctx:
                    await uctx.update(
                        Record("0", data={"features": {"feed": 1}})
                    )
                    await lctx.update(
                        Record("0", data={"features": {"face": 2}})
                    )
                # async with untagged, tagged:
                async with untagged() as uctx, tagged() as lctx:
                    record = await uctx.record("0")
                    self.assertIn("feed", record.features())
                    record = await lctx.record("0")
                    self.assertIn("face", record.features())
            with open(self.testfile, "r") as fd:
                dict_reader = csv.DictReader(fd, dialect="strip")
                rows = {row["tag"]: {row["key"]: row} for row in dict_reader}
                self.assertIn("untagged", rows)
                self.assertIn("sometag", rows)
                self.assertIn("0", rows["untagged"])
                self.assertIn("0", rows["sometag"])
                self.assertIn("feed", rows["untagged"]["0"])
                self.assertIn("face", rows["sometag"]["0"])
                self.assertEqual("1", rows["untagged"]["0"]["feed"])
                self.assertEqual("2", rows["sometag"]["0"]["face"])

    async def test_config_default(self):
        config = CSVSource.config(
            await parse_unknown("--source-csv-filename", "feedface")
        )
        self.assertEqual(config.filename, "feedface")
        self.assertEqual(config.tag, "untagged")
        self.assertEqual(config.tagcol, "tag")
        self.assertEqual(config.key, "key")
        self.assertFalse(config.readwrite)
        self.assertFalse(config.allowempty)
        self.assertIsNone(config.loadfiles)

    async def test_config_set(self):
        config = CSVSource.config(
            await parse_unknown(
                "--source-csv-filename",
                "feedface",
                "--source-csv-tag",
                "default-tag",
                "--source-csv-tagcol",
                "dffml_tag",
                "--source-csv-key",
                "SourceURLColumn",
                "--source-csv-readwrite",
                "--source-csv-allowempty",
                "--source-csv-loadfiles",
            )
        )
        self.assertEqual(config.filename, "feedface")
        self.assertEqual(config.tag, "default-tag")
        self.assertEqual(config.tagcol, "dffml_tag")
        self.assertEqual(config.key, "SourceURLColumn")
        self.assertTrue(config.readwrite)
        self.assertTrue(config.allowempty)
        self.assertTrue(config.loadfiles)

    async def test_key(self):
        with tempfile.TemporaryDirectory() as testdir:
            testfile = os.path.join(testdir, str(random.random()))
            pathlib.Path(testfile).write_text(
                inspect.cleandoc(
                    """
                    KeyHeader,ValueColumn
                    a,42
                    b,420
                    """
                )
            )
            async with CSVSource(
                CSVSourceConfig(filename=testfile, key="KeyHeader")
            ) as source:
                async with source() as sctx:
                    record_a = await sctx.record("a")
                    record_b = await sctx.record("b")
                    self.assertEqual(record_a.feature("ValueColumn"), 42)
                    self.assertEqual(record_b.feature("ValueColumn"), 420)
