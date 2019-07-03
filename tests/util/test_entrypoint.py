# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import unittest
import pkg_resources
from unittest.mock import patch
from typing import Type

from dffml.util.entrypoint import Entrypoint, EntrypointNotFound


class Loadable(object):
    def __init__(self, name: str, parent_class: Type[object]):
        self.name = name
        self.parent_class = parent_class

    def load(self):
        class NewClass(self.parent_class):
            name = self.name

        return NewClass


class FakeEntrypoint(Entrypoint):

    ENTRY_POINT = "fake"


class TestEntrypoint(unittest.TestCase):

    FAKE_ITER = [
        Loadable("one", FakeEntrypoint),
        Loadable("two", object),
        Loadable("three", FakeEntrypoint),
    ]

    def test_load_only_subclasses(self):
        with patch.object(
            pkg_resources, "iter_entry_points", return_value=self.FAKE_ITER
        ) as mock_method:
            loaded = FakeEntrypoint.load()
            self.assertTrue(loaded)
            names = [i.name for i in loaded]
            for should_load in ["one", "three"]:
                with self.subTest(should_load=should_load):
                    self.assertIn(should_load, names)
            with self.subTest(should_not_load="two"):
                self.assertNotIn("two", names)

    def test_load_given_name(self):
        with patch.object(
            pkg_resources, "iter_entry_points", return_value=self.FAKE_ITER
        ) as mock_method:
            loaded = FakeEntrypoint.load("three")
            self.assertEqual("three", loaded.name)

    def test_load_no_found(self):
        with patch.object(
            pkg_resources, "iter_entry_points", return_value=self.FAKE_ITER
        ) as mock_method:
            with self.assertRaises(EntrypointNotFound):
                FakeEntrypoint.load("four")

    def test_load_multiple(self):
        with patch.object(
            pkg_resources, "iter_entry_points", return_value=self.FAKE_ITER
        ) as mock_method:
            loaded = FakeEntrypoint.load_multiple(["one", "three"])
            self.assertTrue(loaded)
            self.assertIn("one", loaded)
            self.assertNotIn("two", loaded)
            self.assertIn("three", loaded)
