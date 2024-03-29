import os
import sys
import zipfile
import tarfile
import tempfile
import contextlib
from unittest.case import TestCase
from unittest.mock import patch, MagicMock
from typing import List

from dffml.df.types import (
    Operation,
    Definition,
    Input,
    DefinitionMissing,
    DataFlow,
    InputFlow,
)
from dffml.df.base import (
    op,
    operation_in,
    opimp_in,
    FailedToLoadOperationImplementation,
    OperationImplementation,
    BaseConfig,
    StringInputSetContext,
    OperationImplementationNotInstantiable,
    OperationImplementationNotInstantiated,
)
from dffml.df.memory import (
    MemoryKeyValueStore,
    MemoryOperationImplementationNetwork,
    MemoryOrchestrator,
    MemoryInputSet,
    MemoryInputSetConfig,
)
from dffml.df.archive import create_archive_dataflow
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

definitions = [
    Definition(name="calc_string", primitive="string"),
    Definition(name="is_add", primitive="bool"),
    Definition(name="is_mult", primitive="bool"),
    Definition(name="numbers", primitive="List[int]"),
    Definition(name="result", primitive="int"),
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)


@op(inputs={"numbers": numbers}, outputs={"sum": result}, conditions=[is_add])
async def add(numbers: List[int]):
    return {"sum": sum(numbers)}


@op(
    inputs={"numbers": numbers},
    outputs={"product": result},
    conditions=[is_mult],
)
async def mult(numbers: List[int]):
    product = 1
    for number in numbers:
        product *= number
    return {"product": product}


@op(
    inputs={"line": calc_string},
    outputs={"add": is_add, "mult": is_mult, "numbers": numbers},
)
async def parse_line(line: str):
    return {
        "add": "add" in line,
        "mult": "mult" in line,
        "numbers": [int(item) for item in line.split() if item.isdigit()],
    }


OPIMPS = opimp_in(sys.modules[__name__])
OPERATIONS = operation_in(sys.modules[__name__])
DATAFLOW = DataFlow.auto(*OPIMPS)


class TestMemoryKeyValueStore(AsyncTestCase):
    async def setUp(self):
        await super().setUp()
        self.kvStore = MemoryKeyValueStore(BaseConfig())

    async def test_get_set(self):
        async with self.kvStore as kvstore:
            async with kvstore() as ctx:
                await ctx.set("feed", b"face")
                self.assertEqual(await ctx.get("feed"), b"face")

    async def test_get_none(self):
        async with self.kvStore as kvstore:
            async with kvstore() as ctx:
                self.assertEqual(await ctx.get("feed"), None)


class TestMemoryOperationImplementationNetwork(AsyncTestCase):
    async def setUp(self):
        await super().setUp()
        self.operationsNetwork = MemoryOperationImplementationNetwork.withconfig(
            {}
        )
        self.operationsNetworkCtx = await self.operationsNetwork.__aenter__()

    async def tearDown(self):
        await super().tearDown()
        await self.operationsNetwork.__aexit__(None, None, None)

    async def test_contains_true(self):
        async with self.operationsNetworkCtx() as ctx:
            await ctx.instantiate(add.op, BaseConfig(), opimp=add.imp)
            self.assertTrue(await ctx.contains(add.op))

    async def test_contains_false(self):
        async with self.operationsNetworkCtx() as ctx:
            self.assertFalse(await ctx.contains(add.op))

    async def test_run(self):
        async with self.operationsNetworkCtx() as ctx:
            await ctx.instantiate(add.op, BaseConfig(), opimp=add.imp)
            # No input set context and input network context required to test
            # the add operation
            self.assertEqual(
                42,
                (await ctx.run(None, None, add.op, {"numbers": [40, 2]}))[
                    "sum"
                ],
            )

    async def test_not_instantiable(self):
        async with self.operationsNetworkCtx() as ctx:
            with self.assertRaises(OperationImplementationNotInstantiable):
                await ctx.run(
                    None,
                    None,
                    add.op._replace(name="add"),
                    {"numbers": [40, 2]},
                )

    async def test_instantiable_but_not_instantiated(self):
        async def return_true(*args, **kwargs):
            return True

        async with self.operationsNetworkCtx() as ctx:
            with self.assertRaises(OperationImplementationNotInstantiated):
                with patch.object(ctx, "instantiable", new=return_true):
                    await ctx.run(None, None, add.op, {"numbers": [40, 2]})


class CustomInputSetContext(StringInputSetContext):
    pass


class TestOrchestrator(AsyncTestCase):
    """
    create_octx and run exist so that we can subclass from them in
    tests/test_high_level.py to test run.
    """

    @contextlib.asynccontextmanager
    async def create_octx(self):
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(DATAFLOW) as octx:
                yield octx

    def run_dataflow(self, octx, *inputs):
        return octx.run(*inputs)

    async def test_run(self):
        calc_strings_check = {"add 40 and 2": 42, "multiply 42 and 10": 420}
        # TODO(p0) Implement and test asyncgenerator
        callstyles_no_expand = [
            "asyncgenerator",
            "dict",
            "dict_custom_input_set_context",
        ]
        callstyles = {
            "dict": {
                to_calc: [
                    Input(
                        value=to_calc, definition=parse_line.op.inputs["line"]
                    ),
                    Input(
                        value=[add.op.outputs["sum"].name],
                        definition=GetSingle.op.inputs["spec"],
                    ),
                ]
                for to_calc in calc_strings_check.keys()
            },
            "dict_custom_input_set_context": {
                CustomInputSetContext(to_calc): [
                    Input(
                        value=to_calc, definition=parse_line.op.inputs["line"]
                    ),
                    Input(
                        value=[add.op.outputs["sum"].name],
                        definition=GetSingle.op.inputs["spec"],
                    ),
                ]
                for to_calc in calc_strings_check.keys()
            },
            "list_input_sets": [
                MemoryInputSet(
                    MemoryInputSetConfig(
                        ctx=StringInputSetContext(to_calc),
                        inputs=[
                            Input(
                                value=to_calc,
                                definition=parse_line.op.inputs["line"],
                            ),
                            Input(
                                value=[add.op.outputs["sum"].name],
                                definition=GetSingle.op.inputs["spec"],
                            ),
                        ],
                    )
                )
                for to_calc in calc_strings_check.keys()
            ],
            "uctx": [
                [
                    Input(
                        value=to_calc, definition=parse_line.op.inputs["line"]
                    ),
                    Input(
                        value=[add.op.outputs["sum"].name],
                        definition=GetSingle.op.inputs["spec"],
                    ),
                ]
                for to_calc in calc_strings_check.keys()
            ],
        }
        async with self.create_octx() as octx:
            for callstyle, inputs in callstyles.items():
                with self.subTest(callstyle=callstyle):
                    if callstyle in callstyles_no_expand:
                        run_coro = self.run_dataflow(octx, inputs)
                    else:
                        run_coro = self.run_dataflow(octx, *inputs)
                    async for ctx, results in run_coro:
                        ctx_str = (await ctx.handle()).as_string()
                        if callstyle == "uctx":
                            self.assertIn(
                                results[add.op.outputs["sum"].name],
                                dict(
                                    zip(
                                        calc_strings_check.values(),
                                        calc_strings_check.keys(),
                                    )
                                ),
                            )
                        else:
                            if callstyle == "dict_custom_input_set_context":
                                self.assertTrue(
                                    isinstance(ctx, CustomInputSetContext)
                                )
                            self.assertEqual(
                                calc_strings_check[ctx_str],
                                results[add.op.outputs["sum"].name],
                            )


class MockIterEntryPoints(AsyncTestCase):
    def iter_entry_points(self, entrypoint):
        for key, value in self.entrypoints[entrypoint].items():
            mock = MagicMock()
            mock.name = key
            mock.load.return_value = value
            yield mock

    async def setUp(self):
        self.exit_stack = contextlib.ExitStack().__enter__()
        self.exit_stack.enter_context(
            patch(
                "pkg_resources.iter_entry_points", new=self.iter_entry_points
            )
        )

    async def tearDown(self):
        self.exit_stack.__exit__(None, None, None)


class TestOperation(MockIterEntryPoints):
    entrypoints = {
        "dffml.operation": {
            "add": add,
            "mult": mult.op,
            "parse_line": parse_line.imp,
        }
    }

    async def test_load(self):
        loaded = Operation.load()
        self.assertIn(add.op, loaded)
        self.assertIn(mult.op, loaded)
        self.assertIn(parse_line.imp.op, loaded)

    async def test_load_name_given(self):
        self.assertEqual(add.op, Operation.load("add"))
        self.assertEqual(mult.op, Operation.load("mult"))
        self.assertEqual(
            parse_line.op._replace(instance_name="parse_line"),
            Operation.load("parse_line")._replace(instance_name="parse_line"),
        )


class TestDataFlow(MockIterEntryPoints):
    def test_export(self):
        exported = DataFlow.auto(add).export(linked=True)
        # Operations
        self.assertIn("operations", exported)
        self.assertIn("tests.test_df:add", exported["operations"])
        self.assertIn("inputs", exported["operations"]["tests.test_df:add"])
        self.assertIn("outputs", exported["operations"]["tests.test_df:add"])
        self.assertIn(
            "conditions", exported["operations"]["tests.test_df:add"]
        )
        self.assertIn(
            "is_add", exported["operations"]["tests.test_df:add"]["conditions"]
        )
        self.assertIn(
            "numbers", exported["operations"]["tests.test_df:add"]["inputs"]
        )
        self.assertEqual(
            "numbers",
            exported["operations"]["tests.test_df:add"]["inputs"]["numbers"],
        )
        self.assertIn(
            "sum", exported["operations"]["tests.test_df:add"]["outputs"]
        )
        self.assertEqual(
            "result",
            exported["operations"]["tests.test_df:add"]["outputs"]["sum"],
        )
        # Definitions
        self.assertIn("definitions", exported)
        self.assertIn("numbers", exported["definitions"])
        self.assertIn("primitive", exported["definitions"]["numbers"])
        self.assertEqual(
            "List[int]", exported["definitions"]["numbers"]["primitive"]
        )
        self.assertIn("result", exported["definitions"])
        self.assertIn("primitive", exported["definitions"]["result"])
        self.assertEqual("int", exported["definitions"]["result"]["primitive"])

    def test_resolve_missing_condition_definition(self):
        exported = DataFlow.auto(add).export(linked=True)
        del exported["definitions"]["is_add"]
        with self.assertRaisesRegex(
            DefinitionMissing, "add.conditions.*is_add"
        ):
            DataFlow._fromdict(**exported)

    def test_resolve_missing_input_output_definition(self):
        exported = DataFlow.auto(add).export(linked=True)
        del exported["definitions"]["result"]
        with self.assertRaisesRegex(DefinitionMissing, "add.outputs.*result"):
            DataFlow._fromdict(**exported)


class TestOperationImplementation(MockIterEntryPoints):
    entrypoints = {
        "dffml.operation": {
            "add": add,
            "mult": mult.imp,
            "parse_line": parse_line.op,
        }
    }

    async def test_load(self):
        loaded = OperationImplementation.load()
        self.assertIn(add.imp, loaded)
        self.assertIn(mult.imp, loaded)
        self.assertNotIn(parse_line.op, loaded)

    async def test_load_name_given(self):
        self.assertEqual(add.imp, OperationImplementation.load("add"))
        self.assertEqual(mult.imp, OperationImplementation.load("mult"))

    async def test_load_failure(self):
        with self.assertRaises(FailedToLoadOperationImplementation):
            OperationImplementation.load("parse_line")


class TestCreateArchiveDataflow(TestCase):
    @property
    def formats_list(self):
        return [
            "tar",
            "tar.gz",
            "tar.bz2",
            "tar.xz",
        ]

    def _create_dataflow(self, input_, output):
        dataflow = create_archive_dataflow(
            {
                Input(
                    value=input_,
                    definition=Definition("test_inp", primitive="str"),
                    origin="input_path",
                ),
                Input(
                    value=output,
                    definition=Definition("test_out", primitive="str"),
                    origin="output_path",
                ),
            }
        )
        return dataflow

    def test_zip_creation_flow(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dataflow = self._create_dataflow(temp_dir, "test_zip.zip")
            self.assertTrue("make_zip_archive" in dataflow.operations.keys())
            self.assertEqual(
                dataflow.flow,
                {
                    "make_zip_archive": InputFlow(
                        inputs={
                            "input_directory_path": ["seed"],
                            "output_file_path": ["seed"],
                        },
                        conditions=[],
                    )
                },
            )

    def test_zip_extraction_flow(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with tempfile.TemporaryDirectory() as input_dir:
                zip_path = os.path.join(output_dir, "test_zip.zip")
                with zipfile.ZipFile(zip_path, "w") as zip:
                    zip.write(input_dir)
            dataflow = self._create_dataflow(zip_path, output_dir)
            self.assertTrue(
                "extract_zip_archive" in dataflow.operations.keys()
            )
            self.assertEqual(
                dataflow.flow,
                {
                    "extract_zip_archive": InputFlow(
                        inputs={
                            "input_file_path": ["seed"],
                            "output_directory_path": ["seed"],
                        },
                        conditions=[],
                    )
                },
            )

    def test_tar_creation_flows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for format_ in self.formats_list:
                dataflow = self._create_dataflow(
                    temp_dir, f"test_tar.{format_}"
                )
                self.assertTrue(
                    "make_tar_archive" in dataflow.operations.keys()
                )
                if format_ != "tar":
                    compression_type = format_.split(".")[1]
                    self.assertTrue(
                        f"{compression_type}_compress"
                        in dataflow.operations.keys()
                    )
                    self.assertEqual(
                        dataflow.flow,
                        {
                            "make_tar_archive": InputFlow(
                                inputs={
                                    "input_directory_path": ["seed"],
                                    "output_file_path": ["seed"],
                                },
                                conditions=[],
                            ),
                            f"{compression_type}_compress": InputFlow(
                                inputs={
                                    "input_file_path": [
                                        {"make_tar_archive": "output_path"}
                                    ],
                                    "output_file_path": ["seed.final_output"],
                                },
                                conditions=[],
                            ),
                        },
                    )
                else:
                    self.assertEqual(
                        dataflow.flow,
                        {
                            "make_tar_archive": InputFlow(
                                inputs={
                                    "input_directory_path": ["seed"],
                                    "output_file_path": ["seed"],
                                },
                                conditions=[],
                            )
                        },
                    )

    def test_tar_extraction_flows(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with tempfile.TemporaryDirectory() as input_dir:
                for format_ in self.formats_list:
                    tar_path = os.path.join(output_dir, f"test_tar.{format_}")
                    with tarfile.open(tar_path, mode="x") as tar:
                        tar.add(input_dir)
                    dataflow = self._create_dataflow(tar_path, output_dir)
                    self.assertTrue(
                        "extract_tar_archive" in dataflow.operations.keys()
                    )
                    if format_ != "tar":
                        compression_type = format_.split(".")[1]
                        self.assertEqual(
                            dataflow.flow,
                            {
                                f"{compression_type}_decompress": InputFlow(
                                    inputs={
                                        "input_file_path": ["seed"],
                                        "output_file_path": ["seed"],
                                    },
                                    conditions=[],
                                ),
                                "extract_tar_archive": InputFlow(
                                    inputs={
                                        "input_file_path": [
                                            {
                                                f"{compression_type}_decompress": "output_path"
                                            }
                                        ],
                                        "output_directory_path": [
                                            "seed.final_output"
                                        ],
                                    },
                                    conditions=[],
                                ),
                            },
                        )
                    else:
                        self.assertEqual(
                            dataflow.flow,
                            {
                                "extract_tar_archive": InputFlow(
                                    inputs={
                                        "input_file_path": ["seed"],
                                        "output_directory_path": ["seed"],
                                    },
                                    conditions=[],
                                )
                            },
                        )
