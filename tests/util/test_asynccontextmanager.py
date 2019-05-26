# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import unittest

from dffml.util.asynchelper import AsyncContextManagerList
from dffml.util.asynctestcase import AsyncTestCase


class OpenCloseTester(object):
    def __init__(self):
        self.isopen = False

    async def __aenter__(self):
        self.isopen = True

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.isopen = False


class TestAsyncContextManagerList(AsyncTestCase):
    async def test_open_close_all(self):
        test_list = AsyncContextManagerList(
            OpenCloseTester(), OpenCloseTester()
        )
        for listel in test_list:
            self.assertFalse(listel.isopen)
        async with test_list:
            for listel in test_list:
                self.assertTrue(listel.isopen)
        for listel in test_list:
            self.assertFalse(listel.isopen)
