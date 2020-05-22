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

ECHO_STRING = """
def echo_string(input_string: str) -> str:
    return "Echo: " + input_string
"""


class TestDataflowCreate(AsyncTestCase):
    @staticmethod
    @contextlib.asynccontextmanager
    async def make_dataflow(ops, operations, seed):
        # Create temp dir and write op to ops.py
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Change directory into the tempdir
            with chdir(tmpdirname):
                # Write out op to op.py
                pathlib.Path(tmpdirname, "ops.py").write_text(ops)
                # $ dffml dataflow create $operations -seed $seed
                with io.StringIO() as dataflow:
                    with contextlib.redirect_stdout(dataflow):
                        await CLI.cli(
                            "dataflow", "create", *operations, "-seed", *seed
                        )
                    yield DataFlow._fromdict(**json.loads(dataflow.getvalue()))

    async def test_single(self):
        operation_qualname = "ops:echo_string"
        async with self.make_dataflow(
            ECHO_STRING,
            [operation_qualname, "get_single"],
            ["ops.echo_string.outputs.result,=get_single_spec"],
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
