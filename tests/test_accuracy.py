# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import unittest

from dffml.accuracy import Accuracy


class TestAccuracry(unittest.TestCase):
    def test_str(self):
        self.assertEqual(str(Accuracy(0.04242)), "4.24")
