from unittest.mock import patch
from typing import NamedTuple

from dffml import (
    run,
    DataFlow,
    GetSingle,
    Input,
    Definition,
    op,
    config,
    OperationException,
)
from dffml.util.cli.arg import Arg, parse_unknown
from dffml.util.entrypoint import entrypoint
from dffml.df.types import Definition, DataFlow, Input
from dffml.df.base import op, BaseKeyValueStore
from dffml.df.memory import (
    MemoryKeyValueStore,
    MemoryRedundancyChecker,
    MemoryRedundancyCheckerConfig,
    MemoryOrchestrator,
)
from dffml.util.asynctestcase import AsyncTestCase


@config
class KeyValueStoreWithArgumentsConfig:
    filename: str


@entrypoint("withargs")
class KeyValueStoreWithArguments(BaseKeyValueStore):

    CONTEXT = NotImplementedError
    CONFIG = KeyValueStoreWithArgumentsConfig

    def __call__(self):
        raise NotImplementedError


def load_kvstore_with_args(loading=None):
    if loading == "withargs":
        return KeyValueStoreWithArguments
    return [KeyValueStoreWithArguments]


class TestMemoryRedundancyChecker(AsyncTestCase):
    @patch.object(BaseKeyValueStore, "load", load_kvstore_with_args)
    def test_args(self):
        self.assertDictEqual(
            MemoryRedundancyChecker.args({}),
            {
                "rchecker": {
                    "plugin": None,
                    "config": {
                        "memory": {
                            "plugin": None,
                            "config": {
                                "kvstore": {
                                    "plugin": Arg(
                                        type=load_kvstore_with_args,
                                        help="Key value store to use",
                                        default=MemoryKeyValueStore(),
                                    ),
                                    "config": {},
                                }
                            },
                        }
                    },
                }
            },
        )

    async def test_config_default_label(self):
        with patch.object(BaseKeyValueStore, "load", load_kvstore_with_args):
            was = MemoryRedundancyChecker.config(
                await parse_unknown(
                    "--rchecker-memory-kvstore",
                    "withargs",
                    "--rchecker-memory-kvstore-withargs-filename",
                    "somefile",
                )
            )
            self.assertEqual(type(was), MemoryRedundancyCheckerConfig)
            self.assertEqual(type(was.kvstore), KeyValueStoreWithArguments)
            self.assertEqual(
                type(was.kvstore.config), KeyValueStoreWithArgumentsConfig
            )
            self.assertEqual(was.kvstore.config.filename, "somefile")


CONDITION = Definition(name="condition", primitive="boolean")


class TestMemoryOrchestrator(AsyncTestCase):
    async def test_condition_does_run(self):
        ran = []

        @op(conditions=[CONDITION])
        async def condition_test(hi: str):
            ran.append(True)

        async with MemoryOrchestrator() as orchestrator:
            async with orchestrator(DataFlow(condition_test)) as octx:
                async for _ in octx.run(
                    [
                        Input(
                            value=True,
                            definition=condition_test.op.inputs["hi"],
                        ),
                        Input(value=True, definition=CONDITION),
                    ]
                ):
                    pass

        self.assertTrue(ran)

    async def test_condition_does_not_run(self):
        ran = []

        @op(conditions=[CONDITION])
        async def condition_test(hi: str):
            ran.append(True)

        async with MemoryOrchestrator() as orchestrator:
            async with orchestrator(DataFlow(condition_test)) as octx:
                async for _ in octx.run(
                    [
                        Input(
                            value=True,
                            definition=condition_test.op.inputs["hi"],
                        ),
                    ]
                ):
                    pass

        self.assertFalse(ran)

    async def test_condition_does_not_run_auto_start(self):
        ran = []

        @op(conditions=[CONDITION])
        async def condition_test():
            ran.append(True)  # pragma: no cover

        async with MemoryOrchestrator() as orchestrator:
            async with orchestrator(DataFlow(condition_test)) as octx:
                async for _ in octx.run([]):
                    pass

        self.assertFalse(ran)


@op(
    outputs={"result": Definition(name="fail_result", primitive="string")},
    retry=3,
)
async def fail_and_retry(self):
    i = getattr(self.parent, "i", 0)
    i += 1
    setattr(self.parent, "i", i)
    if i <= 2:
        raise Exception(f"Failure {i}")
    return {"result": "done"}


class TestMemoryOperationImplementationNetworkContext(AsyncTestCase):
    @staticmethod
    async def run_dataflow(dataflow):
        async for ctx, results in run(
            dataflow,
            [
                Input(
                    value=[fail_and_retry.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
            ],
        ):
            yield results

    async def test_retry_success(self):
        done = False
        async for results in self.run_dataflow(
            DataFlow.auto(fail_and_retry, GetSingle)
        ):
            done = True
            self.assertEqual(results, {"fail_result": "done"})
        self.assertTrue(done)

    async def test_retry_fail(self):
        dataflow = DataFlow(
            GetSingle, operations={"fail_and_retry": fail_and_retry}
        )
        dataflow.operations["fail_and_retry"] = dataflow.operations[
            "fail_and_retry"
        ]._replace(retry=dataflow.operations["fail_and_retry"].retry - 1)

        try:
            async for results in self.run_dataflow(dataflow):
                pass
        except OperationException as error:
            self.assertEqual(error.__cause__.__class__, Exception)
            self.assertEqual(error.__cause__.args[0], "Failure 2")
