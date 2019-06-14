# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
from dffml.source.file import FileSourceConfig
from dffml.source.csv import CSVSource
from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase
from dffml.repo import Repo
import tempfile


class TestCSVSource(SourceTest, AsyncTestCase):
    async def setUpSource(self, fileobj):
        return CSVSource(FileSourceConfig(filename=fileobj.name))


class CSVTest(SourceTest, AsyncTestCase):
    async def setUpSource(self, fileobj):
        return CSVSource(
            FileSourceConfig(filename=fileobj.name, key="classification")
        )

    async def test_key(self):
        repo_with_key = Repo(
            "0",
            data={
                "classification": "2",
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
        set_key = repo_with_key.data.classification

        with tempfile.NamedTemporaryFile() as testfile:
            await self.setUpFile(testfile)
            source = await self.setUpSource(testfile)
            async with source as testSource:
                async with testSource() as sourceContext:
                    await sourceContext.update(repo_with_key)
            async with source as testSource:
                async with testSource() as sourceContext:
                    with self.subTest(src_url=set_key):
                        repo = await sourceContext.repo(set_key)
                        self.assertEqual(
                            repo.src_url, repo_with_key.data.classification
                        )
