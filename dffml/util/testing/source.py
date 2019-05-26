# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import abc
import tempfile

from ...repo import Repo
from ..asynctestcase import AsyncTestCase


class SourceTest(abc.ABC):
    """
    Test case class used to test a Source implementation. Subclass from and set
    the SOURCE property to run tests on that source.

    >>> from dffml.source.file import FileSourceConfig
    >>> from dffml.source.json import JSONSource
    >>> from dffml.util.testing.source import SourceTest
    >>> from dffml.util.asynctestcase import AsyncTestCase
    >>> class TestJSONSource(SourceTest, AsyncTestCase):
    >>>     async def setUpSource(self, fileobj):
    >>>         return JSONSource(FileSourceConfig(filename=fileobj.name))
    """

    async def setUpFile(self, fileobj):
        pass

    @abc.abstractmethod
    async def setUpSource(self, fileobj):
        pass  # pragma: no cover

    async def test_update(self):
        full_src_url = "0"
        empty_src_url = "1"
        full_repo = Repo(
            full_src_url,
            data={
                "classification": "1",
                "features": {
                    "PetalLength": 3.9,
                    "PetalWidth": 1.2,
                    "SepalLength": 5.8,
                    "SepalWidth": 2.7,
                },
                "prediction": {
                    "classification": "feedface",
                    "confidence": 0.42,
                },
            },
        )
        empty_repo = Repo(
            empty_src_url,
            data={
                "classification": "1",
                "features": {
                    "PetalLength": 3.9,
                    "PetalWidth": 1.2,
                    "SepalLength": 5.8,
                    "SepalWidth": 2.7,
                },
            },
        )

        with tempfile.NamedTemporaryFile() as testfile:
            self.maxDiff = 3000
            await self.setUpFile(testfile)
            source = await self.setUpSource(testfile)
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
                        self.assertEqual(
                            repo.data.prediction.classification, "feedface"
                        )
                        self.assertEqual(repo.data.prediction.confidence, 0.42)
                    with self.subTest(src_url=empty_src_url):
                        repo = await sourceContext.repo(empty_src_url)
                        self.assertFalse(repo.data.prediction.classification)
                        self.assertFalse(repo.data.prediction.confidence)
                    with self.subTest(both=[full_src_url, empty_src_url]):
                        repos = {
                            repo.src_url: repo
                            async for repo in sourceContext.repos()
                        }
                        self.assertIn(full_src_url, repos)
                        self.assertIn(empty_src_url, repos)
                        self.assertEqual(
                            repos[full_src_url].features(),
                            full_repo.features(),
                        )
                        self.assertEqual(
                            repos[empty_src_url].features(),
                            empty_repo.features(),
                        )
