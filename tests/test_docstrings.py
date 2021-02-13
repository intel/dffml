import os
import io
import sys
import copy
import shutil
import doctest
import inspect
import pathlib
import asyncio
import logging
import unittest
import tempfile
import platform
import importlib
import contextlib
from typing import Optional, Callable

from dffml import Features, Feature
from dffml.df.types import DataFlow, Input
from dffml.df.memory import MemoryOrchestrator
from dffml.noasync import train
from dffml.model.slr import SLRModel
from dffml.util.asynctestcase import AsyncTestCase
from dffml.db.sqlite import SqliteDatabase, SqliteDatabaseConfig
from dffml.operation.db import db_query_create_table, DatabaseQueryConfig


def modules(
    root: pathlib.Path,
    package_name: str,
    *,
    skip: Optional[Callable[[str, pathlib.Path], bool]] = None,
):
    for path in root.rglob("*.py"):
        # Figure out name
        import_name = pathlib.Path(str(path)[len(str(root)) :]).parts[1:]
        import_name = (
            package_name
            + "."
            + ".".join(
                list(import_name[:-1]) + [import_name[-1].replace(".py", "")]
            )
        )
        # Check if we should skip importing this file
        if skip and skip(import_name, path):
            continue
        # Import module
        yield import_name, importlib.import_module(import_name)


root = pathlib.Path(__file__).parent.parent / "dffml"
skel = root / "skel"
package_name = "dffml"
# Skip any files in skel and __main__.py and __init__.py
skip = lambda _import_name, path: skel in path.parents or path.name.startswith(
    "__"
)

# All classes to test
to_test = {}


@contextlib.contextmanager
def tempdir(state):
    with tempfile.TemporaryDirectory() as new_cwd:
        try:
            orig_cwd = os.getcwd()
            os.chdir(new_cwd)
            yield
        finally:
            os.chdir(orig_cwd)


def wrap_operation_io_AcceptUserInput(state):
    with unittest.mock.patch(
        "builtins.input", return_value="Data flow is awesome"
    ):
        yield


def wrap_high_level_accuracy(state):
    model = SLRModel(
        features=Features(Feature("Years", int, 1),),
        predict=Feature("Salary", int, 1),
        directory="tempdir",
    )

    train(
        model,
        {"Years": 0, "Salary": 10},
        {"Years": 1, "Salary": 20},
        {"Years": 2, "Salary": 30},
        {"Years": 3, "Salary": 40},
    )

    yield


wrap_high_level_predict = wrap_high_level_accuracy


def wrap_noasync_accuracy(state):
    model = SLRModel(
        features=Features(Feature("Years", int, 1),),
        predict=Feature("Salary", int, 1),
        directory="tempdir",
    )

    train(
        model,
        {"Years": 0, "Salary": 10},
        {"Years": 1, "Salary": 20},
        {"Years": 2, "Salary": 30},
        {"Years": 3, "Salary": 40},
    )

    yield


wrap_noasync_predict = wrap_noasync_accuracy


async def operation_db():
    """
    Create the database and table (myTable) for the db operations
    """
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
                "key": "INTEGER NOT NULL PRIMARY KEY",
                "firstName": "text",
                "lastName": "text",
                "age": "int",
            },
            definition=db_query_create_table.op.inputs["cols"],
        ),
    ]

    async for ctx, result in MemoryOrchestrator.run(dataflow, inputs):
        pass


def wrap_operation_db(state):
    asyncio.run(operation_db())
    yield


def wrap_operation_db_db_query_lookup(state):
    run_doctest(operation_db_db_query_insert.obj, state)
    run_doctest(operation_db_db_query_insert_or_update.obj, state, check=False)
    yield


def wrap_operation_db_db_query_update(state):
    run_doctest(operation_db_db_query_insert.obj, state)
    yield


def run_doctest(obj, state, check=True):
    finder = doctest.DocTestFinder(verbose=state["verbose"], recurse=False)
    runner = doctest.DocTestRunner(verbose=state["verbose"])

    for test in finder.find(obj, obj.__qualname__, globs=state["globs"]):
        output = io.StringIO()
        results = runner.run(test, out=output.write)
        if results.failed and check:
            raise Exception(output.getvalue())


def mktestcase(name, import_name, module, obj):
    # Global variables for the doctest
    state = {
        "globs": {},
        "name": name,
        "verbose": os.environ.get("LOGGING", "").lower() == "debug",
    }
    # Check if there is a function within this file which will be used to do
    # extra setup and tear down for the test. Its the same name as the test but
    # prefixed with wrap_. Also look all the way up the path for wrap_ functions
    name = name.split(".")
    extra_context = []
    for i in range(0, len(name)):
        wrapper_name = "wrap_" + "_".join(name[: i + 1])
        wrapper = sys.modules[__name__].__dict__.get(wrapper_name, False)
        if wrapper:
            extra_context.append(contextlib.contextmanager(wrapper))
    # The test case itself, assigned to test_doctest of each class
    def testcase(self):
        if state["verbose"]:
            logging.basicConfig(level=logging.DEBUG)
        with contextlib.ExitStack() as stack:
            # Create tempdir for the test
            stack.enter_context(tempdir(state))
            # Do all test specific setup
            for wrapper in extra_context:
                stack.enter_context(wrapper(state))
            # Run the doctest
            run_doctest(obj, state)

    return testcase


for import_name, module in modules(root, package_name, skip=skip):
    # Iterate over all of the objects in the module
    for name, obj in inspect.getmembers(module):
        # Skip if not a class or function
        if (
            not hasattr(obj, "__module__")
            or not obj.__module__.startswith(import_name)
            or (not inspect.isclass(obj) and not inspect.isfunction(obj))
        ):
            continue
        # Add to dict to ensure no duplicates
        to_test[obj.__module__ + "." + obj.__qualname__] = (
            import_name,
            module,
            obj,
        )
        if inspect.isclass(obj):
            cls = obj
            # Iterate over all of the objects in the class
            for name, obj in inspect.getmembers(cls):
                # Skip if not a class or function
                if (
                    not hasattr(obj, "__module__")
                    or obj.__module__ is None
                    or not obj.__module__.startswith(import_name)
                    or (
                        not inspect.isclass(obj)
                        and not inspect.isfunction(obj)
                    )
                ):
                    continue
                # Add to dict to ensure no duplicates
                to_test[
                    cls.__module__
                    + "."
                    + cls.__qualname__
                    + "."
                    + obj.__qualname__
                ] = (import_name, module, obj)

for name, (import_name, module, obj) in to_test.items():
    # Check that class or function has an example that could be doctested
    docstring = inspect.getdoc(obj)
    if docstring is None or not "\n>>>" in docstring:
        continue
    # Remove the package name from the Python style path to the object
    name = name[len(package_name) + 1 :]
    # Create the test case class. One doctest per class
    testcase = type(
        name.replace(".", "_"),
        (unittest.TestCase,),
        {
            "obj": obj,
            "test_docstring": mktestcase(name, import_name, module, obj),
        },
    )
    # Create the name of the class using the path to it and the object name
    # Add the class to this file's globals
    setattr(sys.modules[__name__], testcase.__qualname__, testcase)

cli_cli_Version_Version_git_hash.test_docstring = unittest.skipIf(
    platform.system() == "Windows",
    "Test cleanup doesn't seem to work on Windows",
)(cli_cli_Version_Version_git_hash.test_docstring)
