# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import io
import atexit
import shutil
import random
import inspect
import asyncio
import logging
import tempfile
import unittest
import collections
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
from dffml.model.model import ModelContext, Model
from dffml.df.types import Operation
from dffml.df.base import OperationImplementation
from dffml.accuracy import Accuracy as AccuracyType
from dffml.util.entrypoint import entry_point
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.cli.cmd import DisplayHelp

from dffml.cli import (
    OperationsAll,
    OperationsRepo,
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
def empty_json_file():
    """
    JSONSource will try to parse a file if it exists and so it needs to be
    given a file with an empty JSON object in it, {}.
    """
    with tempfile.NamedTemporaryFile() as fileobj:
        fileobj.write(b"{}")
        fileobj.seek(0)
        yield fileobj


class ReposTestCase(AsyncTestCase):
    async def setUp(self):
        super().setUp()
        self.repos = [Repo(str(random.random())) for _ in range(0, 10)]
        self.__temp_json_fileobj = empty_json_file()
        self.temp_json_fileobj = self.__temp_json_fileobj.__enter__()
        self.sconfig = FileSourceConfig(filename=self.temp_json_fileobj.name)
        async with JSONSource(self.sconfig) as source:
            async with source() as sctx:
                for repo in self.repos:
                    await sctx.update(repo)

    def tearDown(self):
        super().tearDown()
        self.__temp_json_fileobj.__exit__(None, None, None)


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
    async def train(
        self, sources: Sources, features: Features, classifications: List[Any]
    ):
        pass

    async def accuracy(
        self, sources: Sources, features: Features, classifications: List[Any]
    ) -> AccuracyType:
        return AccuracyType(0.42)

    async def predict(
        self,
        repos: AsyncIterator[Repo],
        features: Features,
        classifications: List[Any],
    ) -> AsyncIterator[Tuple[Repo, Any, float]]:
        async for repo in repos:
            yield repo, "", float(repo.src_url)


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


class TestListRepos(ReposTestCase):
    async def test_run(self):
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            result = await ListRepos.cli(
                "-sources",
                "primary=json",
                "-source-primary-filename",
                self.temp_json_fileobj.name,
                "-source-primary-readonly",
                "false",
            )
            for repo in self.repos:
                self.assertIn(repo.src_url, stdout.getvalue())


class TestOperationsAll(ReposTestCase):
    async def test_run(self):
        self.repo_keys = {"add 40 and 2": 42, "multiply 42 and 10": 420}
        self.repos = list(map(Repo, self.repo_keys.keys()))
        self.temp_json_fileobj.seek(0)
        self.temp_json_fileobj.truncate(0)
        self.temp_json_fileobj.write(b"{}")
        self.temp_json_fileobj.flush()
        async with JSONSource(self.sconfig) as source:
            async with source() as sctx:
                for repo in self.repos:
                    await sctx.update(repo)
        with patch.object(
            OperationImplementation, "load", opimp_load
        ), patch.object(Operation, "load", op_load):
            results = await OperationsAll.cli(
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_json_fileobj.name,
                "-repo-def",
                "calc_string",
                "-remap",
                "get_single.result=string_calculator",
                "-output-specs",
                '["result"]=get_single_spec',
                "-dff-memory-operation-network-ops",
                *map(lambda op: op.name, OPERATIONS),
                "-dff-memory-opimp-network-opimps",
                *map(lambda imp: imp.op.name, OPIMPS),
            )
            results = {
                result.src_url: result.features(["string_calculator"])[
                    "string_calculator"
                ]
                for result in results
            }
            for repo in self.repos:
                self.assertIn(repo.src_url, results)
                self.assertEqual(
                    self.repo_keys[repo.src_url], results[repo.src_url]
                )


class TestOperationsRepo(ReposTestCase):
    async def test_run(self):
        test_key = "multiply 42 and 10"
        self.repo_keys = {"add 40 and 2": 42, "multiply 42 and 10": 420}
        self.repos = list(map(Repo, self.repo_keys.keys()))
        self.temp_json_fileobj.seek(0)
        self.temp_json_fileobj.truncate(0)
        self.temp_json_fileobj.write(b"{}")
        self.temp_json_fileobj.flush()
        async with JSONSource(self.sconfig) as source:
            async with source() as sctx:
                for repo in self.repos:
                    await sctx.update(repo)
        with patch.object(
            OperationImplementation, "load", opimp_load
        ), patch.object(Operation, "load", op_load):
            results = await OperationsRepo.cli(
                "-sources",
                "primary=json",
                "-source-filename",
                self.temp_json_fileobj.name,
                "-keys",
                test_key,
                "-repo-def",
                "calc_string",
                "-remap",
                "get_single.result=string_calculator",
                "-output-specs",
                '["result"]=get_single_spec',
                "-dff-memory-operation-network-ops",
                *map(lambda op: op.name, OPERATIONS),
                "-dff-memory-opimp-network-opimps",
                *map(lambda imp: imp.op.name, OPIMPS),
            )
            self.assertEqual(len(results), 1)
            self.assertEqual(
                self.repo_keys[test_key],
                results[0].features(["string_calculator"])[
                    "string_calculator"
                ],
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
                self.temp_json_fileobj.name,
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
                self.temp_json_fileobj.name,
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
                self.temp_json_fileobj.name,
                "-model",
                "fake",
                "-classifications",
                "misc",
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
                self.temp_json_fileobj.name,
                "-model",
                "fake",
                "-classifications",
                "misc",
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
                self.temp_json_fileobj.name,
                "-model",
                "fake",
                "-classifications",
                "misc",
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
                self.temp_json_fileobj.name,
                "-model",
                "fake",
                "-classifications",
                "misc",
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
