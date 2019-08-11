# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import unittest
import tempfile
import os
import csv
import random
import pathlib

from dffml.source.csv import CSVSource, CSVSourceConfig
from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase
from dffml.repo import Repo
from dffml.util.cli.arg import parse_unknown


class TestCSVSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return CSVSource(CSVSourceConfig(filename=self.testfile))

    async def test_label(self):
        with tempfile.TemporaryDirectory() as testdir:
            self.testfile = os.path.join(testdir, str(random.random()))
            unlabeled = await self.setUpSource()
            labeled = await self.setUpSource()
            labeled.config = labeled.config._replace(label="somelabel")
            async with unlabeled, labeled:
                async with unlabeled() as uctx, labeled() as lctx:
                    await uctx.update(
                        Repo("0", data={"features": {"feed": 1}})
                    )
                    await lctx.update(
                        Repo("0", data={"features": {"face": 2}})
                    )
                # async with unlabeled, labeled:
                async with unlabeled() as uctx, labeled() as lctx:
                    repo = await uctx.repo("0")
                    self.assertIn("feed", repo.features())
                    repo = await lctx.repo("0")
                    self.assertIn("face", repo.features())
            with open(self.testfile, "r") as fd:
                dict_reader = csv.DictReader(fd, dialect="strip")
                rows = {
                    row["label"]: {row["src_url"]: row} for row in dict_reader
                }
                self.assertIn("unlabeled", rows)
                self.assertIn("somelabel", rows)
                self.assertIn("0", rows["unlabeled"])
                self.assertIn("0", rows["somelabel"])
                self.assertIn("feed", rows["unlabeled"]["0"])
                self.assertIn("face", rows["somelabel"]["0"])
                self.assertEqual("1", rows["unlabeled"]["0"]["feed"])
                self.assertEqual("2", rows["somelabel"]["0"]["face"])

    def test_config_default(self):
        config = CSVSource.config(
            parse_unknown("--source-csv-filename", "feedface")
        )
        self.assertEqual(config.filename, "feedface")
        self.assertEqual(config.label, "unlabeled")
        self.assertEqual(config.label_column, "label")
        self.assertEqual(config.key, "src_url")
        self.assertFalse(config.readonly)

    def test_config_set(self):
        config = CSVSource.config(
            parse_unknown(
                "--source-csv-filename",
                "feedface",
                "--source-csv-label",
                "default-label",
                "--source-csv-labelcol",
                "dffml_label",
                "--source-csv-key",
                "SourceURLColumn",
                "--source-csv-readonly",
            )
        )
        self.assertEqual(config.filename, "feedface")
        self.assertEqual(config.label, "default-label")
        self.assertEqual(config.label_column, "dffml_label")
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
                    self.assertEqual(repo_a.feature("ValueColumn"), 42)
                    self.assertEqual(repo_b.feature("ValueColumn"), 420)
