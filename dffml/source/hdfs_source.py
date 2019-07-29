import json
from typing import AsyncIterator, NamedTuple, Dict
from collections import OrderedDict
import os
from hdfs import *

from dffml.base import BaseConfig
from dffml.repo import Repo
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entry_point


class HDFSSourceConfig(BaseConfig, NamedTuple):
    host: str
    port: str
    user: str
    filepath: str
    source: str


@entry_point("dffml.source")
class HDFSSource(BaseSource):

    CONTEXT = BaseSourceContext

    async def __aenter__(self) -> "BaseSource":
        self.client = InsecureClient(
            "http://"+self.config.host+":"+self.config.port,
            user="hadoopuser",
        )
        with self.client.read(self.config.filepath, encoding="utf-8", delimiter="\n") as reader:
           pass
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, "host", Arg(type=str))
        cls.config_set(args, above, "port", Arg(type=str))
        cls.config_set(args, above, "user", Arg(type=str))
        cls.config_set(args, above, "filepath", Arg(type=str))
        cls.config_set(args, above, "source", Arg(type=str))
        return args

    @classmethod
    def config(cls, config, *above):
        return HDFSSourceConfig(
            host=cls.config_get(config, above, "host"),
            port=cls.config_get(config, above, "port"),
            user=cls.config_get(config, above, "user"),
            filepath=cls.config_get(config, above, "filepath"),
            source=cls.config_get(config, above, "source"),
        )
