"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import re
import os
import io
import json
import inspect
import pathlib
import asyncio
import contextlib
import unittest.mock
from typing import Dict, Any

from dffml.repo import Repo
from dffml.base import config
from dffml.df.types import Definition, Operation, DataFlow, Input
from dffml.df.base import op
from dffml.cli.cli import CLI
from dffml.model.model import Model
from dffml.service.dev import Develop
from dffml.util.packaging import is_develop
from dffml.util.entrypoint import load
from dffml.config.config import BaseConfigLoader
from dffml.util.asynctestcase import AsyncTestCase

from .common import IntegrationCLITestCase


class TestList(IntegrationCLITestCase):
    async def test_repos(self):
        src_urls = ["A", "B", "C"]
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "list",
                "repos",
                "-sources",
                "feed=memory",
                "-source-repos",
                *src_urls,
            )
        stdout = self.stdout.getvalue()
        for src_url in src_urls:
            self.assertIn(src_url, stdout)


class TestMerge(IntegrationCLITestCase):
    async def test_memory_to_json(self):
        src_urls = ["A", "B", "C"]
        filename = self.mktempfile()
        await CLI.cli(
            "merge",
            "dest=json",
            "src=memory",
            "-source-dest-filename",
            filename,
            "-source-src-repos",
            *src_urls,
        )
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "list",
                "repos",
                "-sources",
                "tmp=json",
                "-source-tmp-filename",
                filename,
            )
        stdout = self.stdout.getvalue()
        for src_url in src_urls:
            self.assertIn(src_url, stdout)

    async def test_memory_to_csv(self):
        src_urls = ["A", "B", "C"]
        filename = self.mktempfile()
        await CLI.cli(
            "merge",
            "dest=csv",
            "src=memory",
            "-source-dest-filename",
            filename,
            "-source-src-repos",
            *src_urls,
        )
        self.assertEqual(
            pathlib.Path(filename).read_text(),
            inspect.cleandoc(
                """
                src_url,label,prediction,confidence
                A,unlabeled,,
                B,unlabeled,,
                C,unlabeled,,
                """
            )
            + "\n",
        )
