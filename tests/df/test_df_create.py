import io
import pathlib
import tempfile
import contextlib

from dffml.cli import Dataflow
from dffml.util.asynctestcase import AsyncTestCase
from dffml import (
    DataFlow,
    Definition,
    Input,
    op,
    ConfigLoaders,
    MemoryOrchestrator,
    GetSingle,
)

OP_DEF_STRING = """
from dffml import op,Definition

@op(
    inputs={"input_string": Definition(name="InputString", primitive="str")},
    outputs={
        "output_string": Definition(name="OutputString", primitive="str")
    },
)
def echo_string(input_string):
    return {"output_string": input_string}

"""

class TestDataflowCreate(AsyncTestCase):
    async def test_create_from_path(self):
        # creates temp_dir in file path and writes op to ops.py
        with tempfile.TemporaryDirectory(dir = pathlib.Path(__file__).parent) as tmpdirname:
            operation_file_path = pathlib.Path(tmpdirname,"ops.py")
            with open( operation_file_path , 'w+'  ) as operation_file:
                operation_file.write(OP_DEF_STRING)

            operation_qualname = f"tests.df.{pathlib.Path(tmpdirname).name}.ops:echo_string"
            dataflow_file_path = pathlib.Path(tmpdirname,"dataflow.json")

            #   dffml dataflow create -config json \
            #          tests.dt.tmpname.ops:echo_string get_single
            #           > ./tmpname/dataflow.json
            with open(dataflow_file_path,'wb+') as dataflow_file:
                dataflow = io.StringIO()
                with contextlib.redirect_stdout(dataflow):
                    await Dataflow.cli(
                        "create",
                        "-config" "json",
                        *[operation_qualname, "get_single"],
                    )
                dataflow_file.write(dataflow.getvalue().encode())
                dataflow_file.seek(0)

            # loading dataflow from config file
            async with ConfigLoaders() as cfgl:
                _, test_dataflow = await cfgl.load_file(
                    filepath=dataflow_file.name
                )
                test_dataflow = DataFlow._fromdict(**test_dataflow)

            self.assertIn(
                operation_qualname, test_dataflow.operations
            )

            input_string_def = test_dataflow.operations[
                operation_qualname
            ].inputs["input_string"]

            test_dataflow.seed.append(
                Input(
                    value=[input_string_def.name],
                    definition=GetSingle.op.inputs["spec"],
                )
            )
            test_inputs = {
                "TestDataFlowCreate": [
                    Input(
                        value="Irregular at magic school",
                        definition=test_dataflow.operations[
                            operation_qualname
                        ].inputs["input_string"],
                    )
                ]
            }
            async with MemoryOrchestrator.withconfig({}) as orchestrator:
                async with orchestrator(test_dataflow) as octx:
                    async for ctx_str, results in octx.run(test_inputs):
                        self.assertIn("InputString", results)
                        self.assertEqual(
                            results["InputString"], "Irregular at magic school"
                        )
