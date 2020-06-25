import io
import json
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
    BaseConfigLoader, ConfigLoaders,
    INISecret,
    INISecretConfig,
    run
)
from dffml.cli.cli import CLI
from dffml.util.data import export_dict
from dffml.util.asynctestcase import IntegrationCLITestCase

KEY = Definition(name="key", primitive="string")
VALUE = Definition(name="value", primitive="Any")
KEY_DONE = Definition(name="key_done", primitive="string")
VALUE_DONE = Definition(name="value_done", primitive="Any")

@config
class CheckSecretMatchConfig:
    secret: "BaseSecret"

@op(
    inputs={"key": KEY, "value": VALUE},
    outputs={"key_done": KEY_DONE},
    config_cls=CheckSecretMatchConfig,
    imp_enter={"secret": lambda self: self.config.secret},
    ctx_enter={"sctx": lambda self: self.parent.secret()},
)
async def mem_set(self, key, value):
    await self.sctx.set(key, value)
    return {"key_done": key}


@op(
    inputs={"key": KEY_DONE},
    outputs={"value": VALUE_DONE},
    config_cls=CheckSecretMatchConfig,
    imp_enter={"secret": lambda self: self.config.secret},
    ctx_enter={"sctx": lambda self: self.parent.secret()},
)
async def mem_get(self, key):
    value = await self.sctx.get(key)
    return {"value": value}


class TestSharedConfig(IntegrationCLITestCase):
    async def test_shared(self):
        # dataflow = DataFlow.auto(GetSingle, mem_get, mem_set)
        # dataflow.implementations[mem_get.op.name] = mem_get.imp
        # dataflow.implementations[mem_set.op.name] = mem_set.imp

        # shared_name = "shared.MemConfig"

        # temp_secret_file = self.mktempfile(suffix = ".ini")

        # check_secret = CheckSecretMatchConfig(secret=INISecret(
        #     INISecretConfig(filename = temp_secret_file,allowempty = True)))

        # dataflow.shared[shared_name] = check_secret
        # dataflow.configs[mem_get.op.name] = shared_name
        # dataflow.configs[mem_set.op.name] = shared_name

        # dataflow.seed = [
        #     Input(value="code", definition=KEY),
        #     Input(value="geass", definition=VALUE),
        #     Input(
        #         value=[VALUE_DONE.name], definition=GetSingle.op.inputs["spec"]
        #     ),
        # ]

        # dataflow.update()
        # dataflow_file = self.mktempfile(suffix=".yaml")

        # async with BaseConfigLoader.load("yaml").withconfig({}) as configloader:
        #     async with configloader() as loader:
        #         with open(dataflow_file,'wb') as f:
        #             f.write(
        #                 await loader.dumpb(dataflow.export())
        #             )

            # async for ctx,results in run(dataflow):
            #     print(f"ran : {results}")
        dataflow_file = "shared_df.yaml"

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
