# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import pathlib
import unittest
import pkg_resources
from unittest.mock import patch
from typing import Type

from dffml.util.os import chdir
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

    ENTRYPOINT = "fake"


class TestEntrypoint(unittest.TestCase):

    FAKE_ITER = [
        Loadable("one", FakeEntrypoint),
        Loadable("two", object),
        Loadable("three", FakeEntrypoint),
    ]

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

    def test_load_relative(self):
        path = pathlib.Path(__file__).relative_to(os.getcwd())
        path = ".".join(list(path.parts[:-1]) + [path.stem])
        loaded = Entrypoint.load(str(path) + ":FakeEntrypoint")
        self.assertIs(loaded, FakeEntrypoint)
