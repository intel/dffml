# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import abc
import random
import tempfile

from ...repo import Repo
from ..asynctestcase import AsyncTestCase


class SourceTest(abc.ABC):
    """
    Test case class used to test a Source implementation. Subclass from and
    implement the setUpSource method.

    >>> from dffml.source.file import FileSourceConfig
    >>> from dffml.source.json import JSONSource
    >>> from dffml.util.testing.source import SourceTest
    >>> from dffml.util.asynctestcase import AsyncTestCase
    >>> class TestCustomSQliteSource(SourceTest, AsyncTestCase):
    >>>     async def setUpSource(self):
    >>>         return MemorySource(MemorySourceConfig(repos=[Repo('a')]))
    """

    @abc.abstractmethod
    async def setUpSource(self, fileobj):
        pass  # pragma: no cover

    async def test_update(self):
        full_src_url = "0"
        empty_src_url = "1"
        full_repo = Repo(
            full_src_url,
            data={
                "features": {
                    "PetalLength": 3.9,
                    "PetalWidth": 1.2,
                    "SepalLength": 5.8,
                    "SepalWidth": 2.7,
                },
                "prediction": {"value": "feedface", "confidence": 0.42},
            },
        )
        empty_repo = Repo(
            empty_src_url,
            data={
                "features": {
                    "PetalLength": 3.9,
                    "PetalWidth": 1.2,
                    "SepalLength": 5.8,
                    "SepalWidth": 2.7,
                }
            },
        )

        source = await self.setUpSource()
        async with source as testSource:
            # Open, update, and close
            async with testSource() as sourceContext:
                await sourceContext.update(full_repo)
                await sourceContext.update(empty_repo)
        async with source as testSource:
            # Open and confirm we saved and loaded correctly
            async with testSource() as sourceContext:
                with self.subTest(src_url=full_src_url):
                    repo = await sourceContext.repo(full_src_url)
                    self.assertEqual(repo.data.prediction.value, "feedface")
                    self.assertEqual(repo.data.prediction.confidence, 0.42)
                with self.subTest(src_url=empty_src_url):
                    repo = await sourceContext.repo(empty_src_url)
                    self.assertFalse(repo.data.prediction.value)
                    self.assertFalse(repo.data.prediction.confidence)
                with self.subTest(both=[full_src_url, empty_src_url]):
                    repos = {
                        repo.src_url: repo
                        async for repo in sourceContext.repos()
                    }
                    self.assertIn(full_src_url, repos)
                    self.assertIn(empty_src_url, repos)
                    self.assertEqual(
                        repos[full_src_url].features(), full_repo.features()
                    )
                    self.assertEqual(
                        repos[empty_src_url].features(), empty_repo.features()
                    )


class FileSourceTest(SourceTest):
    """
    Test case class used to test a FileSource implementation.

    >>> from dffml.source.file import FileSourceConfig
    >>> from dffml.source.json import JSONSource
    >>> from dffml.util.testing.source import FileSourceTest
    >>> from dffml.util.asynctestcase import AsyncTestCase
    >>> class TestCustomSQliteSource(FileSourceTest, AsyncTestCase):
    >>>     async def setUpSource(self):
    >>>         return JSONSource(FileSourceConfig(filename=self.testfile))
    """

    async def test_update(self):
        with tempfile.TemporaryDirectory() as testdir:
            with self.subTest(extension=None):
                self.testfile = os.path.join(testdir, str(random.random()))
                await super().test_update()
            for extension in ["xz", "gz", "bz2", "lzma", "zip"]:
                with self.subTest(extension=extension):
                    self.testfile = os.path.join(
                        testdir, str(random.random()) + "." + extension
                    )
                    await super().test_update()

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
            async with unlabeled, labeled:
                async with unlabeled() as uctx, labeled() as lctx:
                    repo = await uctx.repo("0")
                    self.assertIn("feed", repo.features())
                    repo = await lctx.repo("0")
                    self.assertIn("face", repo.features())
