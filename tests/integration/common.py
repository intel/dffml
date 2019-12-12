"""
This file contains a class integration tests can derive from. The integration
tests can declare which of the plugins (that are a part of the main repo) they
require to run. The test will be skipped if the plugin isn't installed in
development mode.

To install all plugins in development mode
$ dffml service dev install

Add the -user flag to install to ~/.local
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
from typing import Dict, Any, Optional

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

from ..test_cli import non_existant_tempfile


def relative_path(*args):
    """
    Returns a pathlib.Path object with the path relative to this file.
    """
    target = pathlib.Path(__file__).parents[0] / args[0]
    for path in list(args)[1:]:
        target /= path
    return target


@contextlib.contextmanager
def relative_chdir(*args):
    """
    Change directory to a location relative to the location of this file.
    """
    target = relative_path(*args)
    orig_dir = os.getcwd()
    try:
        os.chdir(target)
        yield target
    finally:
        os.chdir(orig_dir)


class IntegrationCLITestCase(AsyncTestCase):
    REQUIRED_PLUGINS = []

    async def setUp(self):
        super().setUp()
        self.required_plugins(*self.REQUIRED_PLUGINS)
        self.stdout = io.StringIO()
        self._stack = contextlib.ExitStack().__enter__()

    async def tearDown(self):
        super().tearDown()
        self._stack.__exit__(None, None, None)

    def required_plugins(self, *args):
        if not all(map(is_develop, args)):
            self.skipTest(
                f"Required plugins: {', '.join(args)} must be installed in development mode"
            )

    def mktempfile(
        self, suffix: Optional[str] = None, text: Optional[str] = None
    ):
        filename = self._stack.enter_context(non_existant_tempfile())
        if suffix:
            filename = filename + suffix
        if text:
            pathlib.Path(filename).write_text(inspect.cleandoc(text) + "\n")
        return filename
