# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import asyncio
from unittest.mock import patch

from dffml.feature import Feature, Features
from dffml.util.asynctestcase import AsyncTestCase


class TestFeature(AsyncTestCase):
    def setUp(self):
        self.feature = Feature("name", int, 1)

    def test_default_dtype(self):
        self.assertEqual(self.feature.dtype, int)

    def test_default_length(self):
        self.assertEqual(self.feature.length, 1)

    def test_load_def(self):
        # TODO This test should be removed or its name should be modified.
        feature = Feature("test", float, 10)
        self.assertEqual(feature.name, "test")
        self.assertEqual(feature.dtype, float)
        self.assertEqual(feature.length, 10)

    def test_convert_dtype(self):
        self.assertEqual(Feature.convert_dtype("float"), float)

    def test_convert_dtype_invalid(self):
        with self.assertRaisesRegex(TypeError, "Failed to convert"):
            Feature.convert_dtype("not a python data type")


class TestFeatures(AsyncTestCase):
    def setUp(self):
        self.one = Feature("one", int, 1)
        self.two = Feature("two", float, 2)
        self.three = Feature("three", int, 1)
        self.features = Features(self.one, self.two, self.three)

    async def test_names(self):
        names = self.features.names()
        for check in ["one", "two", "three"]:
            self.assertIn(check, names)
