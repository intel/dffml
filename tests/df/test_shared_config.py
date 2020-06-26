import io
import json
import pathlib
import tempfile
import contextlib
from typing import Dict


from dffml import (
    MemoryOrchestrator,
    DataFlow,
    Definition,
    config,
    op,
    BaseDataFlowObject,
    BaseDataFlowObjectContext,
    AsyncTestCase,
    GetSingle,
    Input,
    config,
    BaseConfigLoader,
    ConfigLoaders,
    INISecret,
    INISecretConfig,
    run,
)
from dffml.cli.cli import CLI
from dffml.util.os import chdir
from dffml.util.data import export_dict
from dffml.util.asynctestcase import IntegrationCLITestCase

from .shared_config_ops import mem_get, mem_set, CheckSecretMatchConfig


class TestSharedConfig(IntegrationCLITestCase):
    async def test_shared(self):
        self.required_plugins("dffml-config-yaml")

        # Change to directory where this file is loacted
        self._stack.enter_context(chdir(str(pathlib.Path(__file__).parent)))

        # Create the DataFlow
        dataflow = DataFlow.auto(GetSingle, mem_get, mem_set)
        # Specify targets for shared config. This way we don't have to guess
        # which strings in dataflow.confg are supposed to be coming from shared
        # config
        dataflow.shared["mem_check_secret"] = SharedConfig(
            values=CheckSecretMatchConfig(
                secret=INISecret(
                    INISecretConfig(
                        filename=self.mktempfile(suffix=".ini"),
                        allowempty=True,
                    )
                )
            ),
            targets=[mem_get.op.name, mem_set.op.name,],
        )
        # Add seed inputs
        dataflow.seed = [
            Input(value="code", definition=mem_set.op.inputs["key"]),
            Input(value="geass", definition=mem_set.op.inputs["value"]),
            Input(
                value=[mem_get.op.outputs["value"].name],
                definition=GetSingle.op.inputs["spec"],
            ),
        ]

        # Export the dataflow to a file
        dataflow_file = self.mktempfile(suffix=".yaml")
        async with BaseConfigLoader.load("yaml").withconfig(
            {}
        ) as configloader:
            async with configloader() as loader:
                with open(dataflow_file, "wb") as f:
                    f.write(await loader.dumpb(dataflow.export()))

        # Run the DataFlow
        results = await CLI.cli(
            "dataflow",
            "run",
            "records",
            "all",
            "-no-echo",
            "-dataflow",
            dataflow_file,
            "-sources",
            "m=memory",
            "-source-records",
            "world",
        )
        print(results)
        # self.assertIn("value_done", results)
        # self.assertEqual(results["value_done"], "geass")
