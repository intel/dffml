# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import abc
import random
import tempfile

from ...repo import Repo, RepoPrediction
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
        full_key = "0"
        empty_key = "1"
        full_repo = Repo(
            full_key,
            data={
                "features": {
                    "PetalLength": 3.9,
                    "PetalWidth": 1.2,
                    "SepalLength": 5.8,
                    "SepalWidth": 2.7,
                },
                "prediction": {
                    "target_name": RepoPrediction(
                        value="feedface", confidence=0.42
                    )
                },
            },
        )
        empty_repo = Repo(
            empty_key,
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
                with self.subTest(key=full_key):
                    repo = await sourceContext.repo(full_key)
                    self.assertEqual(
                        repo.data.prediction["target_name"]["value"],
                        "feedface",
                    )
                    self.assertEqual(
                        repo.data.prediction["target_name"]["confidence"], 0.42
                    )
                with self.subTest(key=empty_key):
                    repo = await sourceContext.repo(empty_key)
                    self.assertEqual(
                        [
                            val["value"]
                            for _, val in repo.data.prediction.items()
                        ],
                        ["undetermined"] * (len(repo.data.prediction)),
                    )
                with self.subTest(both=[full_key, empty_key]):
                    repos = {
                        repo.key: repo async for repo in sourceContext.repos()
                    }
                    self.assertIn(full_key, repos)
                    self.assertIn(empty_key, repos)

                    self.assertEqual(
                        repos[full_key].features(), full_repo.features()
                    )
                    self.assertEqual(
                        repos[empty_key].features(), empty_repo.features()
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

    async def test_tag(self):
        with tempfile.TemporaryDirectory() as testdir:
            self.testfile = os.path.join(testdir, str(random.random()))
            untagged = await self.setUpSource()
            tagged = await self.setUpSource()
            tagged.config = tagged.config._replace(tag="sometag")
            async with untagged, tagged:
                async with untagged() as uctx, tagged() as lctx:
                    await uctx.update(
                        Repo("0", data={"features": {"feed": 1}})
                    )
                    await lctx.update(
                        Repo("0", data={"features": {"face": 2}})
                    )
            async with untagged, tagged:
                async with untagged() as uctx, tagged() as lctx:
                    repo = await uctx.repo("0")
                    self.assertIn("feed", repo.features())
                    repo = await lctx.repo("0")
                    self.assertIn("face", repo.features())
