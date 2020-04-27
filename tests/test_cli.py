# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import io
import json
import random
import tempfile
import contextlib
from pathlib import Path
from unittest.mock import patch
from typing import List, AsyncIterator

from dffml.record import Record
from dffml.feature import Feature, Features
from dffml.source.source import Sources
from dffml.source.file import FileSourceConfig
from dffml.source.json import JSONSource
from dffml.source.csv import CSVSource, CSVSourceConfig
from dffml.model.model import ModelContext, Model
from dffml.model.accuracy import Accuracy as AccuracyType
from dffml.util.entrypoint import entrypoint
from dffml.util.asynctestcase import (
    AsyncExitStackTestCase,
    non_existant_tempfile,
)
from dffml.util.cli.cmds import ModelCMD
from dffml.base import config
from dffml.cli import Merge, Dataflow, Train, Accuracy, Predict, List

from .test_df import OPERATIONS, OPIMPS


class RecordsTestCase(AsyncExitStackTestCase):
    async def setUp(self):
        await super().setUp()
        self.records = [Record(str(random.random())) for _ in range(0, 10)]
        self.temp_filename = self.mktempfile()
        self.sconfig = FileSourceConfig(
            filename=self.temp_filename, readwrite=True, allowempty=True
        )
        async with JSONSource(self.sconfig) as source:
            async with source() as sctx:
                for record in self.records:
                    await sctx.update(record)
        contents = json.loads(Path(self.sconfig.filename).read_text())
        # Ensure there are records in the file
        self.assertEqual(
            len(contents.get(self.sconfig.tag)),
            len(self.records),
            "RecordsTestCase JSON file erroneously initialized as empty",
        )
        # TODO(p3) For some reason patching Model.load doesn't work
        # self._stack.enter_context(patch("dffml.model.model.Model.load",
        #     new=model_load))
        self._stack.enter_context(
            patch.object(
                ModelCMD,
                "arg_model",
                new=ModelCMD.arg_model.modify(type=model_load),
            )
        )
        self._stack.enter_context(
            patch("dffml.feature.feature.Feature.load", new=feature_load)
        )
        self._stack.enter_context(
            patch("dffml.df.base.OperationImplementation.load", new=opimp_load)
        )
        self._stack.enter_context(
            patch("dffml.df.types.Operation.load", new=op_load)
        )


@config
class FakeConfig:
    features: Features
    predict: Feature
    directory: str = os.path.join(
        os.path.expanduser("~"), ".cache", "dffml", "test_cli", "fake"
    )


class FakeFeature(Feature):

    NAME: str = "fake"

    def dtype(self):
        return float  # pragma: no cov

    def length(self):
        return 1  # pragma: no cov


class FakeModelContext(ModelContext):
    async def train(self, sources: Sources):
        pass

    async def accuracy(self, sources: Sources) -> AccuracyType:
        return AccuracyType(0.42)

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Record]:
        target = self.parent.config.predict.NAME
        async for record in records:
            record.predicted(target, random.random(), float(record.key))
            yield record


@entrypoint("fake")
class FakeModel(Model):

    CONTEXT = FakeModelContext
    CONFIG = FakeConfig


def feature_load(loading=None):
    if loading == "fake":
        return FakeFeature()
    return [FakeFeature()]


def model_load(loading):
    if loading == "fake":
        return FakeModel
    return [FakeModel]


def op_load(loading):
    return list(filter(lambda op: loading == op.name, OPERATIONS))[0]


def opimp_load(loading=None):
    if loading is not None:
        return list(filter(lambda imp: loading == imp.op.name, OPIMPS))[0]
    return OPIMPS


class TestMerge(RecordsTestCase):
    async def test_json_tag(self):
        await Merge.cli(
            "dest=json",
            "src=json",
            "-source-dest-filename",
            self.temp_filename,
            "-source-dest-tag",
            "sometag",
            "-source-src-filename",
            self.temp_filename,
            "-source-src-allowempty",
            "-source-dest-allowempty",
            "-source-src-readwrite",
            "-source-dest-readwrite",
        )
        # Check the untagged source
        with self.subTest(tagged=None):
            async with JSONSource(
                FileSourceConfig(filename=self.temp_filename)
            ) as source:
                async with source() as sctx:
                    records = [record async for record in sctx.records()]
                    self.assertEqual(len(records), len(self.records))
        # Check the tagged source
        with self.subTest(tagged="sometag"):
            async with JSONSource(
                FileSourceConfig(filename=self.temp_filename, tag="sometag")
            ) as source:
                async with source() as sctx:
                    records = [record async for record in sctx.records()]
                    self.assertEqual(len(records), len(self.records))

    async def test_json_to_csv(self):
        with non_existant_tempfile() as csv_tempfile:
            await Merge.cli(
                "dest=csv",
                "src=json",
                "-source-dest-filename",
                csv_tempfile,
                "-source-dest-key",
                "key",
                "-source-src-filename",
                self.temp_filename,
                "-source-src-allowempty",
                "-source-dest-allowempty",
                "-source-src-readwrite",
                "-source-dest-readwrite",
            )
            contents = Path(csv_tempfile).read_text()
            self.assertEqual(
                contents,
                "key,tag\n"
                + "\n".join(
                    [f"{record.key},untagged" for record in self.records]
                )
                + "\n",
                "Incorrect data in csv file",
            )

    async def test_csv_tag(self):
        with non_existant_tempfile() as csv_tempfile:
            # Move the pre-populated json data to a csv source
            with self.subTest(json_to_csv=True):
                await Merge.cli(
                    "dest=csv",
                    "src=json",
                    "-source-dest-filename",
                    csv_tempfile,
                    "-source-src-filename",
                    self.temp_filename,
                    "-source-src-allowempty",
                    "-source-dest-allowempty",
                    "-source-src-readwrite",
                    "-source-dest-readwrite",
                )
            # Merge one tag to another within the same file
            with self.subTest(merge_same_file=True):
                await Merge.cli(
                    "dest=csv",
                    "src=csv",
                    "-source-dest-filename",
                    csv_tempfile,
                    "-source-dest-tag",
                    "sometag",
                    "-source-src-filename",
                    csv_tempfile,
                    "-source-src-allowempty",
                    "-source-dest-allowempty",
                    "-source-src-readwrite",
                    "-source-dest-readwrite",
                )
            contents = Path(csv_tempfile).read_text()
            self.assertIn("untagged", contents)
            self.assertIn("sometag", contents)
            # Check the untagged source
            with self.subTest(tagged=None):
                async with CSVSource(
                    CSVSourceConfig(filename=csv_tempfile)
                ) as source:
                    async with source() as sctx:
                        records = [record async for record in sctx.records()]
                        self.assertEqual(len(records), len(self.records))
            contents = Path(csv_tempfile).read_text()
            self.assertIn("sometag", contents)
            self.assertIn("untagged", contents)
            # Check the tagged source
            with self.subTest(tagged="sometag"):
                async with CSVSource(
                    CSVSourceConfig(filename=csv_tempfile, tag="sometag")
                ) as source:
                    async with source() as sctx:
                        records = [record async for record in sctx.records()]
                        self.assertEqual(len(records), len(self.records))
            contents = Path(csv_tempfile).read_text()
            self.assertIn("sometag", contents)
            self.assertIn("untagged", contents)


class TestListRecords(RecordsTestCase):
    async def test_run(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = await List.cli(
                "records",
                "-sources",
                "primary=json",
                "-source-primary-filename",
                self.temp_filename,
                "-source-primary-readwrite",
                "true",
            )
        for record in self.records:
            self.assertIn(record.key, stdout.getvalue())


class TestDataflowRunAllRecords(RecordsTestCase):
    async def test_run(self):
        self.record_keys = {"add 40 and 2": 42, "multiply 42 and 10": 420}
        self.records = list(map(Record, self.record_keys.keys()))
        os.unlink(self.temp_filename)
        async with JSONSource(self.sconfig) as source:
            async with source() as sctx:
                for record in self.records:
                    await sctx.update(record)
        with tempfile.NamedTemporaryFile(suffix=".json") as dataflow_file:
            dataflow = io.StringIO()
            with contextlib.redirect_stdout(dataflow):
                await Dataflow.cli(
                    "create",
                    "-config",
                    "json",
                    *map(lambda op: op.name, OPERATIONS),
                )
            dataflow_file.write(dataflow.getvalue().encode())
            dataflow_file.seek(0)
            results = await Dataflow.cli(
                "run",
                "records",
                "all",
                "-dataflow",
                dataflow_file.name,
                "primary=json",
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_filename,
                "-record-def",
                "calc_string",
                "-inputs",
                '["result"]=get_single_spec',
            )
            results = {
                result.key: result.feature("result") for result in results
            }
            for record in self.records:
                self.assertIn(record.key, results)
                self.assertEqual(
                    self.record_keys[record.key], results[record.key]
                )


class TestDataflowRunRecordSet(RecordsTestCase):
    async def test_run(self):
        test_key = "multiply 42 and 10"
        self.record_keys = {"add 40 and 2": 42, "multiply 42 and 10": 420}
        self.records = list(map(Record, self.record_keys.keys()))
        os.unlink(self.temp_filename)
        async with JSONSource(self.sconfig) as source:
            async with source() as sctx:
                for record in self.records:
                    await sctx.update(record)
        with tempfile.NamedTemporaryFile(suffix=".json") as dataflow_file:
            dataflow = io.StringIO()
            with contextlib.redirect_stdout(dataflow):
                await Dataflow.cli(
                    "create",
                    "-config",
                    "json",
                    *map(lambda op: op.name, OPERATIONS),
                )
            dataflow_file.write(dataflow.getvalue().encode())
            dataflow_file.seek(0)
            results = await Dataflow.cli(
                "run",
                "records",
                "set",
                "-keys",
                test_key,
                "-dataflow",
                dataflow_file.name,
                "primary=json",
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_filename,
                "-record-def",
                "calc_string",
                "-inputs",
                '["result"]=get_single_spec',
            )
            self.assertEqual(len(results), 1)
            self.assertEqual(
                self.record_keys[test_key], results[0].feature("result")
            )


class TestTrain(RecordsTestCase):
    async def test_run(self):
        await Train.cli(
            "-sources",
            "primary=json",
            "-source-filename",
            self.temp_filename,
            "-model",
            "fake",
            "-model-features",
            "fake",
            "-model-predict",
            "fake",
        )


class TestAccuracy(RecordsTestCase):
    async def test_run(self):
        result = await Accuracy.cli(
            "-sources",
            "primary=json",
            "-source-filename",
            self.temp_filename,
            "-model",
            "fake",
            "-model-features",
            "fake",
            "-model-predict",
            "fake",
        )
        self.assertEqual(result, 0.42)


class TestPredict(RecordsTestCase):
    async def test_all(self):
        results = await Predict.cli(
            "all",
            "-sources",
            "primary=json",
            "-source-filename",
            self.temp_filename,
            "-model",
            "fake",
            "-model-features",
            "fake",
            "-model-predict",
            "fake",
        )
        results = {
            record.key: record.prediction("fake").confidence
            for record in results
        }
        for record in self.records:
            self.assertEqual(float(record.key), results[record.key])

    async def test_record(self):
        subset = self.records[: (int(len(self.records) / 2))]
        subset_urls = list(map(lambda record: record.key, subset))
        results = await Predict.cli(
            "record",
            "-sources",
            "primary=json",
            "-source-filename",
            self.temp_filename,
            "-model",
            "fake",
            "-model-predict",
            "fake",
            "-model-features",
            "fake",
            "-keys",
            *subset_urls,
        )
        self.assertEqual(len(results), len(subset))
        results = {
            record.key: record.prediction("fake").confidence
            for record in results
        }
        for record in subset:
            self.assertEqual(float(record.key), results[record.key])
