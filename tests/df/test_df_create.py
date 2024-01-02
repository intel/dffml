import io
import os
import sys
import json
import pathlib
import tempfile
import unittest
import importlib
import contextlib

from dffml.cli.cli import CLI
from dffml import (
    DataFlow,
    Input,
    run,
    chdir,
    AsyncTestCase,
)

ECHO_STRING = """
def echo_string(input_string: str) -> str:
    return "Echo: " + input_string
"""

ECHO_STRINGS = """
from typing import AsyncIterator

async def echo_strings(input_string: str) -> AsyncIterator[str]:
    for i in range(0, 5):
        yield f"Echo({i}): {input_string}"
"""


class TestDataflowCreate(AsyncTestCase):
    @staticmethod
    @contextlib.asynccontextmanager
    async def make_dataflow(ops, operations, inputs):
        # Create temp dir and write op to ops.py
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Change directory into the tempdir
            with chdir(tmpdirname):
                # Write out op to op.py
                pathlib.Path(tmpdirname, "ops.py").write_text(ops)
                # Reload contents
                sys.path.insert(0, tmpdirname)
                module = importlib.import_module("ops")
                importlib.reload(module)
                sys.path.pop(0)
                # $ dffml dataflow create $operations -inputs $inputs
                with io.StringIO() as dataflow:
                    with contextlib.redirect_stdout(dataflow):
                        await CLI.cli(
                            "dataflow",
                            "create",
                            *operations,
                            "-inputs",
                            *inputs,
                        )
                    yield DataFlow._fromdict(**json.loads(dataflow.getvalue()))

    async def test_single(self):
        operation_qualname = "ops:echo_string"
        async with self.make_dataflow(
            ECHO_STRING,
            [operation_qualname, "get_single"],
            ["ops:echo_string.outputs.result,=get_single_spec"],
        ) as dataflow:
            # Make sure the operation is in the dataflow
            self.assertIn(operation_qualname, dataflow.operations)
            # Definitions for shorthand access
            idef = dataflow.operations[operation_qualname].inputs[
                "input_string"
            ]
            odef = dataflow.operations[operation_qualname].outputs["result"]
            # Run the dataflow
            async for ctx_str, results in run(
                dataflow,
                [Input(value="Irregular at magic school", definition=idef,)],
            ):
                self.assertIn(odef.name, results)
                self.assertEqual(
                    results[odef.name], "Echo: Irregular at magic school",
                )

    async def test_gen(self):
        operation_qualname = "ops:echo_strings"
        async with self.make_dataflow(
            ECHO_STRINGS,
            [operation_qualname, "get_multi"],
            ["ops:echo_strings.outputs.result,=get_multi_spec"],
        ) as dataflow:
            # Make sure the operation is in the dataflow
            self.assertIn(operation_qualname, dataflow.operations)
            # Definitions for shorthand access
            idef = dataflow.operations[operation_qualname].inputs[
                "input_string"
            ]
            odef = dataflow.operations[operation_qualname].outputs["result"]
            # Run the dataflow
            async for ctx_str, results in run(
                dataflow,
                [Input(value="Irregular at magic school", definition=idef,)],
            ):
                self.assertIn(odef.name, results)
                self.assertListEqual(
                    results[odef.name],
                    [
                        f"Echo({i}): Irregular at magic school"
                        for i in range(0, 5)
                    ],
                )


@unittest.skipIf(
    "DFFML_TEST_FUZZ" in os.environ,
    f"Set DFFML_TEST_FUZZ env var to run fuzz tests",
)
class TestFuzzDataFlowCreate(AsyncTestCase):
    async def test_create(self):
        import atheris

        with atheris.instrument_imports():
            import dffml.df.base
        
        def TestOneInput(data):
            async with self.make_dataflow(
                data.decode(errors='ignore'),
                [operation_qualname, "get_single"],
                ["ops:echo_string.outputs.result,=get_single_spec"],
            ) as _dataflow:
                pass
        
        atheris.Setup([], TestOneInput)
        atheris.Fuzz()
