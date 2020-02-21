# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import asyncio
from unittest.mock import patch

from dffml.feature import Data, Feature, Features, LoggingDict, DefFeature
from dffml.util.asynctestcase import AsyncTestCase


class SingleFeature(Feature):
    def dtype(self):
        return bool  # pragma: no cov

    def length(self):
        return 1  # pragma: no cov


class OneFeatureTester(SingleFeature):
    NAME: str = "one"


class TwoFeatureTester(SingleFeature):
    NAME: str = "two"

    async def calc(self, data: Data) -> bool:
        return True


class TwoBFeatureTester(SingleFeature):
    pass


class ThreeFeatureTester(SingleFeature):
    NAME: str = "three"

    async def applicable(self, data: Data) -> bool:
        return False


class ProgessFeatureTester(SingleFeature):
    NAME: str = "progress"

    async def calc(self, data: Data) -> bool:
        await data.log("Hi")
        return True


class TestLoggingDict(AsyncTestCase):
    def setUp(self):
        self.data = Data("test")
        self.ldict = LoggingDict(self.data)

    def ginternal(self, key):
        return getattr(
            self.ldict, "_%s__dict" % (self.ldict.__class__.__qualname__,)
        )[key]

    async def test_get(self):
        self.assertEqual(await self.ldict.get("feed", default="face"), "face")

    async def test_set(self):
        await self.ldict.set("dead", "beef")
        self.assertEqual(self.ginternal("dead"), "beef")

    async def test_set_ignored(self):
        lock = asyncio.Lock()
        await self.ldict.set("dead", lock)

    async def test_inc(self):
        await self.ldict.set("babe", 0)
        self.assertEqual(self.ginternal("babe"), 0)
        await self.ldict.inc("babe")
        self.assertEqual(self.ginternal("babe"), 1)


class TestData(AsyncTestCase):
    def setUp(self):
        self.data = Data("test")

    async def test_mklock_new(self):
        self.assertNotIn("feed", self.data.locks)
        await self.data.mklock("feed")
        self.assertIn("feed", self.data.locks)

    async def test_mklock_exists(self):
        self.data.locks["feed"] = asyncio.Lock()
        self.assertIn("feed", self.data.locks)
        await self.data.mklock("feed")
        self.assertIn("feed", self.data.locks)

    async def test_results(self):
        async def complete(*args):
            return "face"

        with patch.object(self.data, "complete", complete):
            await self.data.result()
            self.assertEqual(self.data.results, "face")


class TestFeature(AsyncTestCase):
    def setUp(self):
        self.feature = Feature()

    def test_default_dtype(self):
        self.assertEqual(self.feature.dtype(), int)

    def test_default_length(self):
        self.assertEqual(self.feature.length(), 1)

    def test_load_def(self):
        feature = Feature.load_def("test", "float", 10)
        self.assertEqual(feature.NAME, "test")
        self.assertEqual(feature.dtype(), float)
        self.assertEqual(feature.length(), 10)

    def test_convert_dtype(self):
        self.assertEqual(Feature.convert_dtype("float"), float)

    def test_convert_dtype_invalid(self):
        with self.assertRaisesRegex(TypeError, "Failed to convert"):
            Feature.convert_dtype("not a python data type")


class TestDefFeature(AsyncTestCase):
    def test_deffeature(self):
        feature = DefFeature("test", float, 10)
        self.assertEqual(feature.NAME, "test")
        self.assertEqual(feature.dtype(), float)
        self.assertEqual(feature.length(), 10)


class TestFeatures(AsyncTestCase):
    def setUp(self):
        self.one = OneFeatureTester()
        self.two = TwoFeatureTester()
        self.three = ThreeFeatureTester()
        self.features = Features(self.one, self.two, self.three)

    async def test_names(self):
        async with self.features:
            names = self.features.names()
            for check in ["one", "two", "three"]:
                self.assertIn(check, names)
