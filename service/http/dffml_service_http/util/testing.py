import asyncio
import contextlib
from http import HTTPStatus
from unittest.mock import patch
from typing import AsyncIterator

import aiohttp

from dffml import (
    Record,
    config,
    Accuracy,
    Features,
    Feature,
    ModelContext,
    Model,
    Sources,
    SourcesContext,
    entrypoint,
)
from dffml.base import BaseConfig
from dffml.source.memory import MemorySource, MemorySourceConfig

from dffml_service_http.cli import Server
from dffml_service_http.routes import DISALLOW_CACHING


@config
class FakeModelConfig:
    directory: str
    features: Features
    predict: Feature


class FakeModelContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.trained_on: Dict[str, Record] = {}

    async def train(self, sources: Sources):
        async for record in sources.records():
            self.trained_on[record.key] = record

    async def accuracy(self, sources: Sources) -> Accuracy:
        accuracy: int = 0
        async for record in sources.records():
            accuracy += int(record.key)
        return Accuracy(accuracy)

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:
        async for record in sources.with_features(["by_ten"]):
            record.predicted(
                "Salary", record.feature("by_ten") * 10, float(record.key)
            )
            yield record


@entrypoint("fake")
class FakeModel(Model):

    CONTEXT = FakeModelContext
    CONFIG = FakeModelConfig


class ServerRunner:
    def __init__(self):
        self.begin = asyncio.Queue()
        self.end = asyncio.Event()
        self.server_stopped = None

    async def start(self, coro):
        self.server_stopped = asyncio.create_task(coro)
        server_started = asyncio.create_task(self.begin.get())
        done, pending = await asyncio.wait(
            {self.server_stopped, server_started},
            return_when=asyncio.FIRST_COMPLETED,
        )
        # Raise issues if they happened
        for task in done:
            # This branch is only taken if tests fail
            if task is self.server_stopped:  # pragma: no cov
                exception = task.exception()
                if exception is not None:
                    raise exception
        return server_started.result()

    async def stop(self):
        self.end.set()
        await self.server_stopped

    @classmethod
    @contextlib.asynccontextmanager
    async def patch(cls, server_cls):
        self = cls()
        with patch.object(
            server_cls, "RUN_YIELD_START", new=self.begin
        ), patch.object(server_cls, "RUN_YIELD_FINISH", new=self.end):
            yield self
            await self.stop()


class ServerException(Exception):
    pass  # pragma: no cov


class TestRoutesRunning:
    async def setUp(self):
        self.exit_stack = contextlib.AsyncExitStack()
        await self.exit_stack.__aenter__()
        self.tserver = await self.exit_stack.enter_async_context(
            ServerRunner.patch(Server)
        )
        self.cli = Server(port=0, insecure=True)
        await self.tserver.start(self.cli.run())
        # Set up client
        self.session = await self.exit_stack.enter_async_context(
            aiohttp.ClientSession()
        )

    async def tearDown(self):
        await self.exit_stack.__aexit__(None, None, None)

    @property
    def url(self):
        return f"http://{self.cli.addr}:{self.cli.port}"

    def check_allow_caching(self, r):
        for header, should_be in DISALLOW_CACHING.items():
            if not header in r.headers:
                raise Exception(f"No cache header {header} not in {r.headers}")
            if r.headers[header] != should_be:
                raise Exception(
                    f"No cache header {header} should have been {should_be!r} but was {r.headers[header]!r}"
                )

    @contextlib.asynccontextmanager
    async def get(self, path):
        async with self.session.get(self.url + path) as r:
            self.check_allow_caching(r)
            if r.status != HTTPStatus.OK:
                raise ServerException((await r.json())["error"])
            yield r

    @contextlib.asynccontextmanager
    async def post(self, path, *args, **kwargs):
        async with self.session.post(self.url + path, *args, **kwargs) as r:
            self.check_allow_caching(r)
            if r.status != HTTPStatus.OK:
                raise ServerException((await r.json())["error"])
            yield r

    @contextlib.asynccontextmanager
    async def _add_memory_source(self):
        async with MemorySource(
            records=[
                Record(str(i), data={"features": {"by_ten": i * 10}})
                for i in range(0, self.num_records)
            ]
        ) as source:
            self.source = self.cli.app["sources"][self.slabel] = source
            async with source() as sctx:
                self.sctx = self.cli.app["source_contexts"][self.slabel] = sctx
                yield

    @contextlib.asynccontextmanager
    async def _add_fake_model(self):
        async with FakeModel(BaseConfig()) as model:
            self.model = self.cli.app["models"][self.mlabel] = model
            async with model() as mctx:
                self.mctx = self.cli.app["model_contexts"][self.mlabel] = mctx
                yield
