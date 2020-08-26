from unittest.mock import patch
from typing import NamedTuple

from dffml.base import config
from dffml.util.cli.arg import Arg, parse_unknown
from dffml.util.entrypoint import entrypoint
from dffml.df.base import BaseKeyValueStore
from dffml.df.memory import (
    MemoryKeyValueStore,
    MemoryRedundancyChecker,
    MemoryRedundancyCheckerConfig,
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
