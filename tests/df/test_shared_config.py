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
        dataflow = DataFlow.auto(GetSingle, mem_get, mem_set)
        dataflow.implementations[mem_get.op.name] = mem_get.imp
        dataflow.implementations[mem_set.op.name] = mem_set.imp

        shared_name = "mem"

        temp_secret_file = self.mktempfile(suffix=".ini")

        check_secret = CheckSecretMatchConfig(
            secret=INISecret(
                INISecretConfig(filename=temp_secret_file, allowempty=True)
            )
        )

        dataflow.shared[shared_name] = check_secret
        dataflow.configs[mem_get.op.name] = shared_name
        dataflow.configs[mem_set.op.name] = shared_name

        dataflow.seed = [
            Input(value="code", definition=mem_set.op.inputs["key"]),
            Input(value="geass", definition=mem_set.op.inputs["value"]),
            Input(
                value=[mem_get.op.outputs["value"].name],
                definition=GetSingle.op.inputs["spec"],
            ),
        ]

        dataflow.update()

        self._stack.enter_context(chdir(str(pathlib.Path(__file__).parent)))
        dataflow_file = self.mktempfile(suffix=".yaml")

        async with BaseConfigLoader.load("yaml").withconfig(
            {}
        ) as configloader:
            async with configloader() as loader:
                with open(dataflow_file, "wb") as f:
                    f.write(await loader.dumpb(dataflow.export()))

        await CLI.cli(
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
        # results = stdout.getvalue()

        # self.assertIn("value_done", results)
        # self.assertEqual(results["value_done"], "geass")
