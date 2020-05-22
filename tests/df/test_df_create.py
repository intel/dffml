import io
import json
import pathlib
import tempfile
import contextlib

from dffml.cli.cli import CLI
from dffml import (
    DataFlow,
    Definition,
    Input,
    op,
    run,
    GetSingle,
    chdir,
    AsyncTestCase,
)

OP_DEF_STRING = """
def echo_string(input_string: str) -> str:
    return "Echo: " + input_string
"""


class TestDataflowCreate(AsyncTestCase):
    async def test_create_from_path(self):
        # Create temp dir and write op to ops.py
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Change directory into the tempdir
            with chdir(tmpdirname):
                # Write out op to op.py
                operation_file_path = pathlib.Path(tmpdirname, "ops.py")
                operation_file_path.write_text(OP_DEF_STRING)
                # We make the name the path relative to our cwd
                operation_qualname = "ops:echo_string"
                dataflow_file_path = pathlib.Path(tmpdirname, "dataflow.json")
                # $ dffml dataflow create  \
                #    ops:echo_string get_single
                with io.StringIO() as dataflow:
                    with contextlib.redirect_stdout(dataflow):
                        await CLI.cli(
                            "dataflow",
                            "create",
                            *[operation_qualname, "get_single"],
                            "-seed",
                            "ops.echo_string.outputs.result,=get_single_spec",
                        )
                    test_dataflow = DataFlow._fromdict(
                        **json.loads(dataflow.getvalue())
                    )
                # Make sure the operation is in the dataflow
                self.assertIn(operation_qualname, test_dataflow.operations)
                # Definitions for shorthand access
                idef = test_dataflow.operations[operation_qualname].inputs[
                    "input_string"
                ]
                odef = test_dataflow.operations[operation_qualname].outputs[
                    "result"
                ]
                # Run the dataflow
                async for ctx_str, results in run(
                    test_dataflow,
                    [
                        Input(
                            value="Irregular at magic school", definition=idef,
                        )
                    ],
                ):
                    self.assertIn(odef.name, results)
                    self.assertEqual(
                        results[odef.name], "Echo: Irregular at magic school",
                    )
