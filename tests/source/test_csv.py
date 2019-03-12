# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import io
import tempfile
import unittest
import csv
from unittest.mock import patch, mock_open
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator

from dffml.repo import Repo
from dffml.source import Source, CSVSource
from dffml.util.asynctestcase import AsyncTestCase

class TestCSVSource(AsyncTestCase):

    async def test_update(self):
        repo = Repo("24",data= {
            "classification": "1",
            "features": {
                "PetalLength": 3.9,
                "PetalWidth": 1.2,
                "SepalLength": 5.8,
                "SepalWidth": 2.7,
            },
            "last_updated": "2019-03-11T09:11:25Z",
            "prediction": {
                "classification": "1",
                "confidence": 1.0
            },
        })
        csvSource = CSVSource(os.path.join(
                os.path.expanduser('~'), '.cache', 'dffml_test.csv'))
        csvSource.mem["22"] = repo
        fd, path = tempfile.mkstemp()
        
        with os.fdopen(fd, 'w') as tmp:
            await csvSource.dump_fd(tmp)
        print("Temporary file path :" + path)

        with open(path,'r') as rd:
            headers = csv.DictReader(rd).fieldnames
            self.assertTrue(set(['prediction','confidence']).issubset(set(headers)))





