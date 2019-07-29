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
    source: BaseSource.load


@entry_point("dffml.source")
class HDFSSource(BaseSource):

    CONTEXT = BaseSourceContext

    async def __aenter__(self) -> "BaseSource":
        self.client = InsecureClient(
            "http://" + self.config.host + ":" + self.config.port,
            user="hadoopuser",
        )
        with self.client.read(self.config.filepath, encoding="utf-8") as fd:
            await self.config.source.load_fd(fd)
        return self

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, "host", Arg(type=str))
        cls.config_set(args, above, "port", Arg(type=str))
        cls.config_set(args, above, "user", Arg(type=str))
        cls.config_set(args, above, "filepath", Arg(type=str))
        cls.config_set(args, above, "source", Arg(type=BaseSource.load))
        for loaded in BaseSource.load():
            loaded.args(args, *cls.add_orig_label(*above))
        return args

    @classmethod
    def config(cls, config, *above):
        source = cls.config_get(config, above, "source")
        source = source.withconfig(config, *cls.add_label(*above))
        source._open = cls.__aenter__.__get__(source)
        return HDFSSourceConfig(
            host=cls.config_get(config, above, "host"),
            port=cls.config_get(config, above, "port"),
            user=cls.config_get(config, above, "user"),
            filepath=cls.config_get(config, above, "filepath"),
            source=source,
        )
