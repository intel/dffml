# This file is used as a header in every file that is created to run each
# example when the doctests are run.
import os
import sys
import shutil
import atexit
import inspect
import asyncio
import tempfile
import builtins
import functools
from unittest import mock

# Create a temporary directory for test to run in
DOCTEST_TEMPDIR = tempfile.mkdtemp()
# Remove it when the test exits
atexit.register(functools.partial(shutil.rmtree, DOCTEST_TEMPDIR))
# Change the current working directory to the temporary directory
os.chdir(DOCTEST_TEMPDIR)

from dffml import *
from dffml.base import *
from dffml.record import *
from dffml.df.base import *
from dffml.df.types import *
from dffml.util.net import *
from dffml.df.memory import *
from dffml_model_scikit import *
from dffml.operation.io import *
from dffml.source.memory import *
from dffml.operation.output import *
from dffml.operation.dataflow import *
from dffml.operation.preprocess import *

# Used for mocking input() for AcceptUserInput operation.
mock.patch("builtins.input", return_value="Data flow is awesome").start()
