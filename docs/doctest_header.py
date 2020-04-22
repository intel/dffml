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

from dffml import *
from dffml.base import *
from dffml.record import *
from dffml.df.base import *
from dffml.df.types import *
from dffml.util.net import *
from dffml.df.memory import *
from dffml.model.slr import *
from dffml_model_scikit import *
from dffml.operation.io import *
from dffml.source.memory import *
from dffml.operation.model import *
from dffml.operation.output import *
from dffml.operation.dataflow import *
from dffml.operation.preprocess import *
from dffml.operation.mapping import *
from dffml.operation.db import *
from dffml.db.sqlite import *


# Create a temporary directory for test to run in
DOCTEST_TEMPDIR = tempfile.mkdtemp()
# Remove it when the test exits
atexit.register(functools.partial(shutil.rmtree, DOCTEST_TEMPDIR))
# Change the current working directory to the temporary directory
os.chdir(DOCTEST_TEMPDIR)

# Creating sqlite db and using create_table query for `operation/db` examples.

sdb = SqliteDatabase(SqliteDatabaseConfig(filename="examples.db"))

dataflow = DataFlow(
    operations={"db_query_create": db_query_create_table.op},
    configs={"db_query_create": DatabaseQueryConfig(database=sdb)},
    seed=[],
)

inputs = [
    Input(
        value="myTable",
        definition=db_query_create_table.op.inputs["table_name"],
    ),
    Input(
        value={
            "key": "real",
            "firstName": "text",
            "lastName": "text",
            "age": "real",
        },
        definition=db_query_create_table.op.inputs["cols"],
    ),
]


async def main():
    async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
        pass


asyncio.run(main())

#

# Used for mocking input() for AcceptUserInput operation.
mock.patch("builtins.input", return_value="Data flow is awesome").start()
