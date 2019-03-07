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
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator

from dffml.repo import Repo
from dffml.feature import Feature, Features
from dffml.source import Sources, RepoSource
from dffml.model import Model
from dffml.accuracy import Accuracy as AccuracyType
from dffml.util.asynctestcase import AsyncTestCase

from dffml.cli import EvaluateAll, EvaluateRepo, \
        Train, Accuracy, PredictAll, PredictRepo

class ReposTestCase(AsyncTestCase):

    def setUp(self):
        self.repos = [Repo(str(random.random())) for _ in range(0, 10)]
        self.sources = Sources(RepoSource(*self.repos))
        self.features = Features(FakeFeature())

class FakeFeature(Feature):

    NAME: str = 'fake'

    def dtype(self):
        return float # pragma: no cov

    def length(self):
        return 1 # pragma: no cov

    async def applicable(self, data):
        return True

    async def fetch(self, data):
        pass

    async def parse(self, data):
        pass

    async def calc(self, data):
        return float(data.src_url)

class FakeModel(Model):

    async def train(self, sources: Sources, features: Features,
            classifications: List[Any], steps: int, num_epochs: int):
        pass

    async def accuracy(self, sources: Sources, features: Features,
            classifications: List[Any]) -> AccuracyType:
        return AccuracyType(1.00)

    async def predict(self, repos: AsyncIterator[Repo], features: Features,
            classifications: List[Any]) -> \
                    AsyncIterator[Tuple[Repo, Any, float]]:
        async for repo in repos:
            yield repo, '', 1.0

class TestEvaluateAll(ReposTestCase):

    def setUp(self):
        super().setUp()
        self.cli = EvaluateAll(sources=self.sources, features=self.features)

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.repos))
        for repo in self.repos:
            self.assertIn(repo.src_url, repos)
            self.assertIn('fake', repos[repo.src_url].features())
            self.assertEqual(float(repo.src_url),
                    repos[repo.src_url].features(['fake'])['fake'])

class TestEvaluateRepo(ReposTestCase):

    def setUp(self):
        super().setUp()
        self.subset = self.repos[int(len(self.repos) / 2):]
        self.cli = EvaluateRepo(sources=self.sources, features=self.features,
                keys=[repo.src_url for repo in self.subset])

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.subset))
        for repo in self.subset:
            self.assertIn(repo.src_url, repos)
            self.assertIn('fake', repos[repo.src_url].features())
            self.assertEqual(float(repo.src_url),
                    repos[repo.src_url].features(['fake'])['fake'])

class TestTrain(AsyncTestCase):

    def setUp(self):
        self.cli = Train(model=FakeModel(), model_dir=None,
                sources=Sources(RepoSource()), features=Features())

    async def test_run(self):
        await self.cli.run()

class TestAccuracy(AsyncTestCase):

    def setUp(self):
        self.cli = Accuracy(model=FakeModel(),
                sources=Sources(RepoSource()), features=Features())

    async def test_run(self):
        self.assertEqual(1.0, await self.cli.run())

class TestPredictAll(ReposTestCase):

    def setUp(self):
        super().setUp()
        self.cli = PredictAll(model=FakeModel(), sources=self.sources,
                features=self.features)

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.repos))
        for repo in self.repos:
            self.assertIn(repo.src_url, repos)

class TestPredictRepo(ReposTestCase):

    def setUp(self):
        super().setUp()
        self.subset = self.repos[int(len(self.repos) / 2):]
        self.cli = PredictRepo(model=FakeModel(), sources=self.sources,
                features=self.features,
                keys=[repo.src_url for repo in self.subset])

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.subset))
        for repo in self.subset:
            self.assertIn(repo.src_url, repos)
