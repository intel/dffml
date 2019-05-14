# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import tempfile

from ...repo import Repo
from ..asynctestcase import AsyncTestCase

class SourceTest(object):
    '''
    Test case class used to test a Source implementation. Subclass from and set
    the SOURCE property to run tests on that source.

    >>> from dffml.source import JSONSource
    >>> from dffml.util.testing.source import SourceTest
    >>> from dffml.util.asynctestcase import AsyncTestCase
    >>> class TestJSONSource(SourceTest, AsyncTestCase):
    >>>     SOURCE = JSONSource
    '''

    async def setUpFile(self, fileobj):
        pass

    async def test_update(self):
        full_src_url = '0'
        empty_src_url = '1'
        full_repo = Repo(full_src_url, data= {
            "classification": "1",
            "features": {
                "PetalLength": 3.9,
                "PetalWidth": 1.2,
                "SepalLength": 5.8,
                "SepalWidth": 2.7,
            },
            "prediction": {
                "classification": "feedface",
                "confidence": 0.42
            },
        })
        empty_repo = Repo(empty_src_url, data= {
            "classification": "1",
            "features": {
                "PetalLength": 3.9,
                "PetalWidth": 1.2,
                "SepalLength": 5.8,
                "SepalWidth": 2.7,
            },
        })

        with tempfile.NamedTemporaryFile() as testfile:
            await self.setUpFile(testfile)
            testSource = self.SOURCE(testfile.name)
            # Open, update, and close
            async with testSource as source:
                await source.update(full_repo)
                await source.update(empty_repo)
            # Open and confirm we saved and loaded correctly
            async with testSource as source:
                with self.subTest(src_url=full_src_url):
                    repo = await source.repo(full_src_url)
                    self.assertEqual(repo.data.prediction.classification,
                                     "feedface")
                    self.assertEqual(repo.data.prediction.confidence, 0.42)
                with self.subTest(src_url=empty_src_url):
                    repo = await source.repo(empty_src_url)
                    self.assertFalse(repo.data.prediction.classification)
                    self.assertFalse(repo.data.prediction.confidence)
