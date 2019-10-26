# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import io
import json
import atexit
import shutil
import random
import inspect
import asyncio
import logging
import tempfile
import unittest
import contextlib
import collections
from pathlib import Path
from unittest.mock import patch
from functools import wraps
from contextlib import contextmanager, ExitStack
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator

from dffml.repo import Repo
from dffml.feature import Feature, Features, DefFeature
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.source.file import FileSourceConfig
from dffml.source.json import JSONSource
from dffml.source.csv import CSVSource, CSVSourceConfig
from dffml.model.model import ModelContext, Model
from dffml.df.types import Operation
from dffml.df.base import OperationImplementation
from dffml.accuracy import Accuracy as AccuracyType
from dffml.util.entrypoint import entry_point
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.cli.cmd import DisplayHelp

from dffml.cli import (
    Merge,
    Dataflow,
    EvaluateAll,
    EvaluateRepo,
    Train,
    Accuracy,
    PredictAll,
    PredictRepo,
    ListRepos,
)

from .test_df import OPERATIONS, OPIMPS


@contextmanager
def non_existant_tempfile():
    """
    Yield the filename of a non-existant file within a temporary directory
    """
    with tempfile.TemporaryDirectory() as testdir:
        yield os.path.join(testdir, str(random.random()))


class ReposTestCase(AsyncTestCase):
    async def setUp(self):
        super().setUp()
        self.repos = [Repo(str(random.random())) for _ in range(0, 10)]
        self.__stack = ExitStack()
        self._stack = self.__stack.__enter__()
        self.temp_filename = self.mktempfile()
        self.sconfig = FileSourceConfig(filename=self.temp_filename)
        async with JSONSource(self.sconfig) as source:
            async with source() as sctx:
                for repo in self.repos:
                    await sctx.update(repo)
        contents = json.loads(Path(self.sconfig.filename).read_text())
        # Ensure there are repos in the file
        self.assertEqual(
            len(contents.get(self.sconfig.label)),
            len(self.repos),
            "ReposTestCase JSON file erroneously initialized as empty",
        )

    def tearDown(self):
        super().tearDown()
        self.__stack.__exit__(None, None, None)

    def mktempfile(self):
        return self._stack.enter_context(non_existant_tempfile())


class FakeFeature(Feature):

    NAME: str = "fake"

    def dtype(self):
        return float  # pragma: no cov

    def length(self):
        return 1  # pragma: no cov

    async def applicable(self, data):
        return True

    async def fetch(self, data):
        pass

    async def parse(self, data):
        pass

    async def calc(self, data):
        return float(data.src_url)


class FakeModelContext(ModelContext):
    async def train(self, sources: Sources):
        pass

    async def accuracy(self, sources: Sources) -> AccuracyType:
        return AccuracyType(0.42)

    async def predict(self, repos: AsyncIterator[Repo]) -> AsyncIterator[Repo]:
        async for repo in repos:
            repo.predicted(random.random(), float(repo.src_url))
            yield repo


@entry_point("fake")
class FakeModel(Model):

    CONTEXT = FakeModelContext


def feature_load(loading):
    return FakeFeature()


def model_load(loading):
    return FakeModel


def op_load(loading):
    return list(filter(lambda op: loading == op.name, OPERATIONS))[0]


def opimp_load(loading=None):
    if loading is not None:
        return list(filter(lambda imp: loading == imp.op.name, OPIMPS))[0]
    return OPIMPS


class TestMerge(ReposTestCase):
    async def test_json_label(self):
        await Merge.cli(
            "dest=json",
            "src=json",
            "-source-dest-filename",
            self.temp_filename,
            "-source-dest-label",
            "somelabel",
            "-source-src-filename",
            self.temp_filename,
        )
        # Check the unlabeled source
        with self.subTest(labeled=None):
            async with JSONSource(
                FileSourceConfig(filename=self.temp_filename)
            ) as source:
                async with source() as sctx:
                    repos = [repo async for repo in sctx.repos()]
                    self.assertEqual(len(repos), len(self.repos))
        # Check the labeled source
        with self.subTest(labeled="somelabel"):
            async with JSONSource(
                FileSourceConfig(
                    filename=self.temp_filename, label="somelabel"
                )
            ) as source:
                async with source() as sctx:
                    repos = [repo async for repo in sctx.repos()]
                    self.assertEqual(len(repos), len(self.repos))

    async def test_json_to_csv(self):
        with non_existant_tempfile() as csv_tempfile:
            await Merge.cli(
                "dest=csv",
                "src=json",
                "-source-dest-filename",
                csv_tempfile,
                "-source-dest-key",
                "src_url",
                "-source-src-filename",
                self.temp_filename,
            )
            contents = Path(csv_tempfile).read_text()
            self.assertEqual(
                contents,
                "src_url,label,prediction,confidence\n"
                + "\n".join(
                    [f"{repo.src_url},unlabeled,," for repo in self.repos]
                )
                + "\n",
                "Incorrect data in csv file",
            )

    async def test_csv_label(self):
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
                )
            # Merge one label to another within the same file
            with self.subTest(merge_same_file=True):
                await Merge.cli(
                    "dest=csv",
                    "src=csv",
                    "-source-dest-filename",
                    csv_tempfile,
                    "-source-dest-label",
                    "somelabel",
                    "-source-src-filename",
                    csv_tempfile,
                )
            contents = Path(csv_tempfile).read_text()
            self.assertIn("unlabeled", contents)
            self.assertIn("somelabel", contents)
            # Check the unlabeled source
            with self.subTest(labeled=None):
                async with CSVSource(
                    CSVSourceConfig(filename=csv_tempfile)
                ) as source:
                    async with source() as sctx:
                        repos = [repo async for repo in sctx.repos()]
                        self.assertEqual(len(repos), len(self.repos))
            contents = Path(csv_tempfile).read_text()
            self.assertIn("somelabel", contents)
            self.assertIn("unlabeled", contents)
            # Check the labeled source
            with self.subTest(labeled="somelabel"):
                async with CSVSource(
                    CSVSourceConfig(filename=csv_tempfile, label="somelabel")
                ) as source:
                    async with source() as sctx:
                        repos = [repo async for repo in sctx.repos()]
                        self.assertEqual(len(repos), len(self.repos))
            contents = Path(csv_tempfile).read_text()
            self.assertIn("somelabel", contents)
            self.assertIn("unlabeled", contents)


class TestListRepos(ReposTestCase):
    async def test_run(self):
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            result = await ListRepos.cli(
                "-sources",
                "primary=json",
                "-source-primary-filename",
                self.temp_filename,
                "-source-primary-readonly",
                "false",
            )
            for repo in self.repos:
                self.assertIn(repo.src_url, stdout.getvalue())


class TestDataflowRunAllRepos(ReposTestCase):
    async def test_run(self):
        self.repo_keys = {"add 40 and 2": 42, "multiply 42 and 10": 420}
        self.repos = list(map(Repo, self.repo_keys.keys()))
        os.unlink(self.temp_filename)
        async with JSONSource(self.sconfig) as source:
            async with source() as sctx:
                for repo in self.repos:
                    await sctx.update(repo)
        with patch.object(
            OperationImplementation, "load", opimp_load
        ), patch.object(
            Operation, "load", op_load
        ), tempfile.NamedTemporaryFile(
            suffix=".json"
        ) as dataflow_file:
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
                "repos",
                "all",
                "-dataflow",
                dataflow_file.name,
                "primary=json",
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_filename,
                "-repo-def",
                "calc_string",
                "-inputs",
                '["result"]=get_single_spec',
            )
            results = {
                result.src_url: result.feature("result") for result in results
            }
            for repo in self.repos:
                self.assertIn(repo.src_url, results)
                self.assertEqual(
                    self.repo_keys[repo.src_url], results[repo.src_url]
                )


class TestDataflowRunRepoSet(ReposTestCase):
    async def test_run(self):
        test_key = "multiply 42 and 10"
        self.repo_keys = {"add 40 and 2": 42, "multiply 42 and 10": 420}
        self.repos = list(map(Repo, self.repo_keys.keys()))
        os.unlink(self.temp_filename)
        async with JSONSource(self.sconfig) as source:
            async with source() as sctx:
                for repo in self.repos:
                    await sctx.update(repo)
        with patch.object(
            OperationImplementation, "load", opimp_load
        ), patch.object(
            Operation, "load", op_load
        ), tempfile.NamedTemporaryFile(
            suffix=".json"
        ) as dataflow_file:
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
                "repos",
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
                "-repo-def",
                "calc_string",
                "-inputs",
                '["result"]=get_single_spec',
            )
            self.assertEqual(len(results), 1)
            self.assertEqual(
                self.repo_keys[test_key], results[0].feature("result")
            )


class TestEvaluateAll(ReposTestCase):
    async def test_run(self):
        with patch.object(
            EvaluateAll,
            "arg_features",
            EvaluateRepo.arg_features.modify(type=feature_load),
        ):
            results = await EvaluateAll.cli(
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_filename,
                "-features",
                "fake",
            )
            results = {
                result.src_url: result.features(["fake"])["fake"]
                for result in results
            }
            for repo in self.repos:
                self.assertIn(repo.src_url, results)
                self.assertEqual(float(repo.src_url), results[repo.src_url])


class TestEvaluateRepo(TestEvaluateAll):
    async def test_run(self):
        subset = self.repos[: (int(len(self.repos) / 2))]
        with patch.object(
            EvaluateRepo,
            "arg_features",
            EvaluateRepo.arg_features.modify(type=feature_load),
        ):
            subset_urls = list(map(lambda repo: repo.src_url, subset))
            results = await EvaluateRepo.cli(
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_filename,
                "-features",
                "fake",
                "-keys",
                *subset_urls,
            )
            self.assertEqual(len(results), len(subset))
            results = {
                result.src_url: result.features(["fake"])["fake"]
                for result in results
            }
            for repo in subset:
                self.assertIn(repo.src_url, results)
                self.assertEqual(float(repo.src_url), results[repo.src_url])


class TestTrain(ReposTestCase):
    async def test_run(self):
        with patch.object(
            Train, "arg_model", Train.arg_model.modify(type=model_load)
        ), patch.object(
            Train, "arg_features", Train.arg_features.modify(type=feature_load)
        ):
            await Train.cli(
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_filename,
                "-model",
                "fake",
                "-features",
                "fake",
            )


class TestAccuracy(TestTrain):
    async def test_run(self):
        with patch.object(
            Accuracy, "arg_model", Accuracy.arg_model.modify(type=model_load)
        ), patch.object(
            Accuracy,
            "arg_features",
            Accuracy.arg_features.modify(type=feature_load),
        ):
            result = await Accuracy.cli(
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_filename,
                "-model",
                "fake",
                "-features",
                "fake",
            )
            self.assertEqual(result, 0.42)


class TestPredictAll(ReposTestCase):
    async def test_run(self):
        with patch.object(
            PredictAll,
            "arg_model",
            PredictAll.arg_model.modify(type=model_load),
        ), patch.object(
            PredictAll,
            "arg_features",
            PredictAll.arg_features.modify(type=feature_load),
        ):
            results = await PredictAll.cli(
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_filename,
                "-model",
                "fake",
                "-features",
                "fake",
            )
            results = {
                repo.src_url: repo.prediction().confidence for repo in results
            }
            for repo in self.repos:
                self.assertEqual(float(repo.src_url), results[repo.src_url])


class TestPredictRepo(ReposTestCase):
    async def test_run(self):
        subset = self.repos[: (int(len(self.repos) / 2))]
        with patch.object(
            PredictRepo,
            "arg_model",
            PredictRepo.arg_model.modify(type=model_load),
        ), patch.object(
            PredictRepo,
            "arg_features",
            PredictRepo.arg_features.modify(type=feature_load),
        ):
            subset_urls = list(map(lambda repo: repo.src_url, subset))
            results = await PredictRepo.cli(
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_filename,
                "-model",
                "fake",
                "-features",
                "fake",
                "-keys",
                *subset_urls,
            )
            self.assertEqual(len(results), len(subset))
            results = {
                repo.src_url: repo.prediction().confidence for repo in results
            }
            for repo in subset:
                self.assertEqual(float(repo.src_url), results[repo.src_url])
