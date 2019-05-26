# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import unittest
from typing import List

from dffml.util.tempdir import TempDir
from dffml.util.asynctestcase import AsyncTestCase


class TestTempDir(unittest.TestCase):
    def test_mktempdir(self):
        dirname = TempDir().mktempdir()
        self.assertEqual(os.path.isdir(dirname), True)
        os.rmdir(dirname)

    def test_rmtempdirs(self):
        tempdir = TempDir()
        dirname = tempdir.mktempdir()
        self.assertEqual(os.path.isdir(dirname), True)
        tempdir.rmtempdirs()
        self.assertEqual(os.path.isdir(dirname), False)


class TestTempDirAsyncContextManager(AsyncTestCase):
    async def test_removes_on_aexit(self):
        length: int = 10
        dirs: List[str] = []
        tempdir: TempDir = TempDir()
        async with tempdir:
            for _i in range(0, length):
                dirs.append(tempdir.mktempdir())
                self.assertTrue(os.path.isdir(dirs[-1]))
        self.assertEqual(len(dirs), length)
        for dirname in dirs:
            self.assertFalse(os.path.exists(dirname))
