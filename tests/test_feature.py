# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import asyncio
from unittest.mock import patch

from dffml.feature import Feature, Features, DefFeature
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


class TwoBFeatureTester(SingleFeature):
    pass


class ThreeFeatureTester(SingleFeature):
    NAME: str = "three"


class ProgessFeatureTester(SingleFeature):
    NAME: str = "progress"


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
        names = self.features.names()
        for check in ["one", "two", "three"]:
            self.assertIn(check, names)
