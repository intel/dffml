"""
WARNING Adding too many testcases to this file starts causing weird errors where
pkgresources will try to __import__ a package and then that pacakge won't be
found. It only happens when there's too many testcases in one file, which is why
test_integration_cli.py was split into a directory. Also, it will only happen
when all the testcases in the file are run at once. Not when running only the
testcase that fails by itself. It's very werid.
"""
import re
import json
import pathlib
import contextlib

from dffml.df.types import Operation, DataFlow, Input
from dffml.cli.cli import CLI
from dffml.util.entrypoint import load
from dffml.configloader.configloader import BaseConfigLoader, ConfigLoaders
from dffml.util.asynctestcase import IntegrationCLITestCase, relative_path


class TestDataFlow(IntegrationCLITestCase):

    REQUIRED_PLUGINS = ["shouldi", "dffml-config-yaml", "dffml-feature-git"]

    async def setUp(self):
        await super().setUp()
        # Use shouldi's dataflow for tests
        self.DATAFLOW = list(load("shouldi.cli:DATAFLOW"))[0]


class TestDataFlowDiagram(TestDataFlow):
    async def test_default(self):
        filename = self.mktempfile() + ".json"
        pathlib.Path(filename).write_text(json.dumps(self.DATAFLOW.export()))
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli("dataflow", "diagram", filename)
        stdout = self.stdout.getvalue()
        # Check that a subgraph is being made for each operation
        self.assertTrue(re.findall(r"subgraph.*run_bandit", stdout))
        # Check that all stages are included
        for check in ["Processing", "Output", "Cleanup"]:
            self.assertIn(f"{check} Stage", stdout)

    async def test_simple(self):
        filename = self.mktempfile() + ".json"
        pathlib.Path(filename).write_text(json.dumps(self.DATAFLOW.export()))
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli("dataflow", "diagram", "-simple", filename)
        # Check that a subgraph is not being made for each operation
        self.assertFalse(
            re.findall(r"subgraph.*run_bandit", self.stdout.getvalue())
        )

    async def test_single_stage(self):
        filename = self.mktempfile() + ".json"
        pathlib.Path(filename).write_text(json.dumps(self.DATAFLOW.export()))
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "dataflow", "diagram", "-stages", "processing", "--", filename
            )
        stdout = self.stdout.getvalue()
        # Check that the single stage is not its own subgraph
        for check in ["Processing", "Output", "Cleanup"]:
            self.assertNotIn(f"{check} Stage", stdout)

    async def test_multi_stage(self):
        filename = self.mktempfile() + ".json"
        pathlib.Path(filename).write_text(json.dumps(self.DATAFLOW.export()))
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "dataflow",
                "diagram",
                "-stages",
                "processing",
                "output",
                "--",
                filename,
            )
        stdout = self.stdout.getvalue()
        # Check that the single stage is not its own subgraph
        for check in ["Processing", "Output"]:
            self.assertIn(f"{check} Stage", stdout)
        for check in ["Cleanup"]:
            self.assertNotIn(f"{check} Stage", stdout)


class TestDataFlowMerge(TestDataFlow):
    async def test_dataflow_usage_example(self):
        # Write out shouldi dataflow
        orig = self.mktempfile() + ".json"
        pathlib.Path(orig).write_text(json.dumps(self.DATAFLOW.export()))
        # Import from feature/git
        transform_to_record = Operation.load("dffml.mapping.create")
        lines_of_code_by_language, lines_of_code_to_comments = list(
            load(
                "dffml_feature_git.feature.operations:lines_of_code_by_language",
                "dffml_feature_git.feature.operations:lines_of_code_to_comments",
                relative=relative_path("..", "..", "feature", "git"),
            )
        )
        # Create new dataflow
        override = DataFlow.auto(
            transform_to_record,
            lines_of_code_by_language,
            lines_of_code_to_comments,
        )
        # TODO Modify and compare against yaml in docs example
        # Write out override dataflow
        created = self.mktempfile() + ".json"
        pathlib.Path(created).write_text(json.dumps(override.export()))
        # Merge the two
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli("dataflow", "merge", orig, created)
        DataFlow._fromdict(**json.loads(self.stdout.getvalue()))

    async def test_run(self):
        self.required_plugins("dffml-config-yaml", "dffml-model-scratch")
        # Load get_single and model_predict
        get_single = Operation.load("get_single")
        model_predict = list(load("dffml.operation.model:model_predict"))[0]
        # Create new dataflow from operations
        dataflow = DataFlow.auto(get_single, model_predict)
        # Add the seed inputs
        dataflow.seed.append(
            Input(
                value=[
                    definition.name
                    for definition in model_predict.op.outputs.values()
                ],
                definition=get_single.inputs["spec"],
            )
        )
        # Write out the dataflow
        dataflow_yaml = pathlib.Path(self.mktempfile() + ".yaml")
        async with BaseConfigLoader.load("yaml").withconfig(
            {}
        ) as configloader:
            async with configloader() as loader:
                dataflow_yaml.write_bytes(
                    await loader.dumpb(dataflow.export(linked=True))
                )
        # TODO Figure out how nested model config options will work
        # print(dataflow_yaml.read_text())
        return


class TestDataFlowCreate(TestDataFlow):
    async def test_dataflow_run_cli_example(self):
        # Write out override dataflow
        created = self.mktempfile() + ".yaml"
        with open(created, "w") as fileobj:
            with contextlib.redirect_stdout(fileobj):
                await CLI.cli(
                    "dataflow",
                    "create",
                    "dffml.mapping.create",
                    "print_output",
                    "-configloader",
                    "yaml",
                )
        # Load the generated dataflow
        async with ConfigLoaders() as cfgl:
            _, exported = await cfgl.load_file(created)
            dataflow = DataFlow._fromdict(**exported)
        # Modify the dataflow
        dataflow.flow["print_output"].inputs["data"] = [
            {"dffml.mapping.create": "mapping"}
        ]
        # Write back modified dataflow
        async with BaseConfigLoader.load("yaml").withconfig(
            {}
        ) as configloader:
            async with configloader() as loader:
                with open(created, "wb") as fileobj:
                    fileobj.write(
                        await loader.dumpb(dataflow.export(linked=True))
                    )
        # Run the dataflow
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "dataflow",
                "run",
                "records",
                "all",
                "-no-echo",
                "-record-def",
                "value",
                "-inputs",
                "hello=key",
                "-dataflow",
                created,
                "-sources",
                "m=memory",
                "-source-records",
                "world",
                "user",
            )
        self.assertEqual(
            self.stdout.getvalue(), "{'hello': 'world'}\n{'hello': 'user'}\n"
        )
