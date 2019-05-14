# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
from dffml.source import CSVSource
from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase

class TestCSVSource(SourceTest, AsyncTestCase):

    SOURCE = CSVSource
