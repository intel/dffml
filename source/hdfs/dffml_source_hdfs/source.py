import json
from typing import AsyncIterator, NamedTuple, Dict
from collections import OrderedDict
import os
from contextlib import AsyncExitStack
from hdfs import *

from dffml.base import BaseConfig
from dffml.repo import Repo
from dffml.source.file import FileSource
from dffml.source.source import BaseSourceContext, BaseSource
from dffml.util.cli.arg import Arg
from dffml.util.entrypoint import entry_point


class HDFSSourceConfig(BaseConfig, NamedTuple):
    host: str
    port: int
    user: str
    filepath: str
    source: FileSource


@entry_point("dffml.source")
class HDFSSource(BaseSource):

    CONTEXT = BaseSourceContext
    async def __aenter__(self) -> "BaseSource":
        self.client = client = InsecureClient(
            "http://" + self.config.host + ":" + self.config.port,
            user="hadoopuser",
        )

        async def new_open(self):
            with client.read(self.config.filepath, encoding="utf-8") as fd:
                await self.load_fd(fd)

        async def new_close(self):
            with client.write(self.config.filepath, encoding="utf-8", overwrite=True) as fd:
                await self.dump_fd(fd)

        self.config.source._open = self.new_open.__get__(self.config.source, self.config.source.__class__)
        self.config.source._close = self.new_close.__get__(self.config.source, self.config.source.__class__)
        self.__stack = AsyncExitStack()
        await self.__stack.__aenter__()
        self.source = await self.__stack.enter_async_context(self.config.source)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.__stack is not None:
            await self.__stack.__aexit__(exc_type, exc_value, traceback)
            self.__stack = None
        return self

    def __call__(self) -> BaseSourceContext:
        return self.source()

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, "host", Arg(type=str))
        cls.config_set(args, above, "port", Arg(type=int))
        cls.config_set(args, above, "user", Arg(type=str))
        cls.config_set(args, above, "filepath", Arg(type=str))
        cls.config_set(args, above, "source", Arg(type=FileSource))
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
