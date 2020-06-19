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
    run,
)
from typing import Dict


@config
class SharedMemoryKeyValueStoreConfig:
    name: str


class SharedMemoryKeyValueStoreContext(BaseDataFlowObjectContext):
    def __init__(self, parent):
        self.parent = parent

    async def set(self, key, value):
        self.parent.mem[key] = value

    async def get(self, key):
        return self.parent.mem[key]


class SharedMemoryKeyValueStore(BaseDataFlowObject):
    CONTEXT = SharedMemoryKeyValueStoreContext
    CONFIG = SharedMemoryKeyValueStoreConfig

    def __init__(self, config):
        super().__init__(config)
        self.mem = {}

    def __call__(self):
        return self.CONTEXT(self)


@config
class MemConfig:
    mem: SharedMemoryKeyValueStore


KEY = Definition(name="key", primitive="string")
VALUE = Definition(name="value", primitive="Any")
KEY_DONE = Definition(name="key_done", primitive="string")
VALUE_DONE = Definition(name="value_done", primitive="Any")


@op(
    inputs={"key": KEY, "value": VALUE},
    outputs={"key_done": KEY_DONE},
    config_cls=MemConfig,
    imp_enter={"mem": lambda self: self.config.mem},
    ctx_enter={"memctx": lambda self: self.parent.mem()},
)
async def mem_set(self, key, value):
    await self.memctx.set(key, value)
    return {"key_done": key}


@op(
    inputs={"key": KEY_DONE},
    outputs={"value": VALUE_DONE},
    config_cls=MemConfig,
    imp_enter={"mem": lambda self: self.config.mem},
    ctx_enter={"memctx": lambda self: self.parent.mem()},
)
async def mem_get(self, key):
    value = await self.memctx.get(key)
    return {"value": value}


class TestSharedConfig(AsyncTestCase):
    async def test_shared(self):
        dataflow = DataFlow.auto(GetSingle, mem_get, mem_set)
        dataflow.implementations[mem_get.op.name] = mem_get.imp
        dataflow.implementations[mem_set.op.name] = mem_set.imp

        shared_name = "shared.MemConfig"
        dataflow.shared[shared_name] = MemConfig(
            mem=SharedMemoryKeyValueStore(name="Lelouch")
        )
        dataflow.configs[mem_get.op.name] = shared_name
        dataflow.configs[mem_set.op.name] = shared_name

        dataflow.seed = [
            Input(value="code", definition=KEY),
            Input(value="geass", definition=VALUE),
            Input(
                value=[VALUE_DONE.name], definition=GetSingle.op.inputs["spec"]
            ),
        ]

        async for ctx, results in run(dataflow):
            self.assertIn("value_done", results)
            self.assertEqual(results["value_done"], "geass")
