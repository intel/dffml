import os
import json
import uuid
import secrets
import traceback
from functools import wraps, partial
from http import HTTPStatus
from functools import partial
from dataclasses import dataclass
from contextlib import AsyncExitStack
from typing import List, Union, AsyncIterator, Type, NamedTuple, Dict

from aiohttp import web
import aiohttp_cors

from dffml.repo import Repo
from dffml.base import BaseConfig, MissingConfig
from dffml.df.types import DataFlow, Input
from dffml.source.source import BaseSource
from dffml.df.memory import MemoryOrchestrator
from dffml.util.entrypoint import EntrypointNotFound
from dffml.df.base import OperationImplementationNotInstantiable


# TODO Add test for this
# Bits of randomness in secret tokens
SECRETS_TOKEN_BITS = 384
SECRETS_TOKEN_BYTES = int(SECRETS_TOKEN_BITS / 8)


OK = {"error": None}
SOURCE_NOT_LOADED = {"error": "Source not loaded"}
MULTICOMM_NOT_LOADED = {"error": "MutliComm not loaded"}


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except:
            if isinstance(obj, type):
                return obj.__qualname__
            return str(obj)  # pragma: no cov


@dataclass
class IterkeyEntry:
    """
    iterkeys will hold the first repo within the next iteration and ths
    iterator. The first time around the first repo is None, since we haven't
    iterated yet. We do this because if the chunk_size is the same as the number
    of iterations then we'll need to iterate one time more than chunk_size in
    order to hit the StopAsyncIteration exception.
    """

    first: Union[Repo, None]
    repos: AsyncIterator[Repo]


def mcctx_route(handler):
    """
    Ensure that the labeled multicomm context requested is loaded. Return the
    mcctx if it is loaded and an error otherwise.
    """

    @wraps(handler)
    async def get_mcctx(self, request):
        mcctx = request.app["multicomm_contexts"].get(
            request.match_info["label"], None
        )
        if mcctx is None:
            return web.json_response(
                MULTICOMM_NOT_LOADED, status=HTTPStatus.NOT_FOUND
            )
        return await handler(self, request, mcctx)

    return get_mcctx


def sctx_route(handler):
    """
    Ensure that the labeled sctx requested is loaded. Return the sctx
    if it is loaded and an error otherwise.
    """

    @wraps(handler)
    async def get_sctx(self, request):
        sctx = request.app["source_contexts"].get(
            request.match_info["label"], None
        )
        if sctx is None:
            return web.json_response(
                SOURCE_NOT_LOADED, status=HTTPStatus.NOT_FOUND
            )
        return await handler(self, request, sctx)

    return get_sctx


class HTTPChannelConfig(NamedTuple):
    path: str
    presentation: str
    asynchronous: bool
    dataflow: DataFlow

    @classmethod
    def _fromdict(cls, **kwargs):
        kwargs["dataflow"] = DataFlow._fromdict(**kwargs["dataflow"])
        return cls(**kwargs)


class Routes:
    PRESENTATION_OPTIONS = ["json", "blob", "text"]

    async def get_registered_handler(self, request):
        return self.app["multicomm_routes"].get(request.path, None)

    async def multicomm_dataflow(self, config, request):
        # Seed the network with inputs given by caller
        # TODO allow list of valid definitions to seed
        # TODO convert inputs into Input instances
        inputs = []
        # If data was sent add those inputs
        if request.method == "POST":
            # Accept a list of input data
            for input_data in await request.json():
                # TODO validate that input data is list and each item has definition
                # and value properties
                if (
                    not input_data["definition"]["name"]
                    in config.dataflow.definitions
                ):
                    return web.json_response(
                        {
                            "error": f"Missing definition for {input_data['definition']['name']} in dataflow"
                        },
                        status=HTTPStatus.NOT_FOUND,
                    )
                inputs.append(
                    Input(
                        value=input_data["value"],
                        definition=config.dataflow.definitions[
                            input_data["definition"]["name"]
                        ],
                    )
                )
        # Run the operation in an orchestrator
        # TODO Create the orchestrator on startup of the HTTP API itself
        async with MemoryOrchestrator.basic_config() as orchestrator:
            async with orchestrator() as octx:
                result = await octx.run_dataflow(
                    config.dataflow, inputs=inputs
                )
                if config.presentation == "blob":
                    return web.Response(body=result)
                elif config.presentation == "text":
                    return web.Response(text=result)
                else:
                    return web.json_response(result)

    async def multicomm_dataflow_asynchronous(self, config, request):
        # TODO allow list of valid definitions to seed
        raise NotImplementedError(
            "asynchronous data flows not yet implemented"
        )
        if (
            headers.get("connection", "").lower() == "upgrade"
            and headers.get("upgrade", "").lower() == "websocket"
            and req.method == "GET"
        ):
            ws_server = web.WebSocketResponse()
            await ws_server.prepare(req)
            self.loop.create_task(
                asyncio.wait(
                    [
                        self.wsforward(ws_server, ws_client),
                        self.wsforward(ws_client, ws_server),
                    ],
                    return_when=asyncio.FIRST_COMPLETED,
                )
            )
            return ws_server
        else:
            # TODO http/2
            return web.json_response(
                {"error": f"Must use websockets"},
                status=HTTPStatus.UPGRADE_REQUIRED,
            )

    @web.middleware
    async def error_middleware(self, request, handler):
        try:
            # HACK This checks if aiohttp's builtin not found handler is going
            # to be called
            # Check if handler is the not found handler
            if "Not Found" in str(handler):
                # Run get_registered_handler to see if we can find the handler
                new_handler = await self.get_registered_handler(request)
                if new_handler is not None:
                    handler = new_handler
            return await handler(request)
        except web.HTTPException as error:
            return web.json_response(
                {"error": error.reason}, status=error.status
            )
        except Exception as error:  #  pragma: no cov
            self.logger.error(
                "ERROR handling %s: %s",
                request,
                traceback.format_exc().strip(),
            )
            return web.json_response(
                {"error": "Internal Server Error"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    async def service_upload(self, request):
        if self.upload_dir is None:
            return web.json_response(
                {"error": "Uploads not allowed"},
                status=HTTPStatus.NOT_IMPLEMENTED,
                headers={"Cache-Control": "no-cache"},
            )

        filepath = os.path.abspath(
            os.path.join(self.upload_dir, request.match_info["filepath"])
        )

        if not filepath.startswith(os.path.abspath(self.upload_dir)):
            return web.json_response(
                {"error": "Attempted path traversal"},
                status=HTTPStatus.BAD_REQUEST,
            )

        reader = await request.multipart()

        field = await reader.next()
        if field.name != "file":
            return web.json_response(
                {"error": "Missing 'file' field"},
                status=HTTPStatus.BAD_REQUEST,
            )

        # Can't rely on Content-Length if transfer is chunked.
        size = 0
        with open(filepath, "wb") as f:
            while True:
                chunk = await field.read_chunk()  # 8192 bytes by default.
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

        return web.json_response(OK)

    async def list_sources(self, request):
        return web.json_response(
            {
                source.ENTRY_POINT_ORIG_LABEL: source.args({})
                for source in BaseSource.load()
            },
            dumps=partial(json.dumps, cls=JSONEncoder),
        )

    async def configure_source(self, request):
        source_name = request.match_info["source"]
        label = request.match_info["label"]

        config = await request.json()

        try:
            source = BaseSource.load_labeled(f"{label}={source_name}")
        except EntrypointNotFound as error:
            self.logger.error(
                f"/configure/source/ failed to load source: {error}"
            )
            return web.json_response(
                {"error": f"source {source_name} not found"},
                status=HTTPStatus.NOT_FOUND,
            )

        try:
            source = source.withconfig(config)
        except MissingConfig as error:
            return web.json_response(
                {"error": str(error)}, status=HTTPStatus.BAD_REQUEST
            )

        # DFFML objects all follow a double context entry pattern
        exit_stack = request.app["exit_stack"]
        source = await exit_stack.enter_async_context(source)
        request.app["sources"][label] = source
        sctx = await exit_stack.enter_async_context(source())
        request.app["source_contexts"][label] = sctx

        return web.json_response(OK)

    def register_config(self) -> Type[HTTPChannelConfig]:
        return HTTPChannelConfig

    async def register(self, config: HTTPChannelConfig) -> None:
        if config.asynchronous:
            handler = self.multicomm_dataflow_asynchronous
        else:
            handler = self.multicomm_dataflow
        self.app["multicomm_routes"][config.path] = partial(handler, config)

    @mcctx_route
    async def multicomm_register(self, request, mcctx):
        config = mcctx.register_config()._fromdict(**(await request.json()))
        if config.presentation not in self.PRESENTATION_OPTIONS:
            return web.json_response(
                {
                    "error": f"{config.presentation!r} is not a valid presentation option: {self.PRESENTATION_OPTIONS!r}"
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        self.logger.debug("Register new mutlicomm route: %r", config)
        await mcctx.register(config)
        return web.json_response(OK)

    @sctx_route
    async def source_repo(self, request, sctx):
        return web.json_response(
            (await sctx.repo(request.match_info["key"])).dict()
        )

    @sctx_route
    async def source_update(self, request, sctx):
        await sctx.update(
            Repo(request.match_info["key"], data=await request.json())
        )
        return web.json_response(OK)

    async def _iter_repos(self, iterkey, chunk_size) -> List[Repo]:
        """
        Iterates over a repos async generator and returns a list with chunk_size
        or less repos in it (if iteration completed). It also returns the
        iterkey, which will be None if iteration completed.
        """
        if not iterkey in self.app["source_repos_iterkeys"]:
            raise web.HTTPNotFound(reason="iterkey not found")
        entry = self.app["source_repos_iterkeys"][iterkey]
        # Make repo_list start with the last repo that was retrieved from
        # iteration the last time _iter_repos was called. If this is the first
        # time then repo_list is an empty list
        repo_list = [entry.first] if entry.first is not None else []
        # We need to iterate one more time than chunk_size the first time
        # _iter_repos is called so that we return the chunk_size and set
        # entry.first for the subsequent iterations
        iter_until = chunk_size + 1 if not repo_list else chunk_size
        for i in range(0, iter_until):
            try:
                # On last iteration make the repo the first repo in the next
                # iteration
                if i == (iter_until - 1):
                    entry.first = await entry.repos.__anext__()
                else:
                    repo_list.append(await entry.repos.__anext__())
            except StopAsyncIteration:
                # If we're done iterating over repos and can remove the
                # reference to the iterator from iterkeys
                del self.app["source_repos_iterkeys"][iterkey]
                iterkey = None
                break
        return iterkey, repo_list

    @sctx_route
    async def source_repos(self, request, sctx):
        iterkey = secrets.token_hex(nbytes=SECRETS_TOKEN_BYTES)
        # TODO Add test that iterkey is removed on last iteration
        self.app["source_repos_iterkeys"][iterkey] = IterkeyEntry(
            first=None, repos=sctx.repos()
        )
        iterkey, repos = await self._iter_repos(
            iterkey, int(request.match_info["chunk_size"])
        )
        return web.json_response(
            {
                "iterkey": iterkey,
                "repos": {repo.src_url: repo.dict() for repo in repos},
            }
        )

    @sctx_route
    async def source_repos_iter(self, request, sctx):
        iterkey, repos = await self._iter_repos(
            request.match_info["iterkey"],
            int(request.match_info["chunk_size"]),
        )
        return web.json_response(
            {
                "iterkey": iterkey,
                "repos": {repo.src_url: repo.dict() for repo in repos},
            }
        )

    async def on_shutdown(self, app):
        self.logger.debug("Shutting down service and exiting all contexts")
        await app["exit_stack"].__aexit__(None, None, None)

    async def setup(self, **kwargs):
        self.app = web.Application(middlewares=[self.error_middleware])
        if self.cors_domains:
            self.cors = aiohttp_cors.setup(
                self.app,
                defaults={
                    domain: aiohttp_cors.ResourceOptions(
                        allow_headers=("Content-Type",)
                    )
                    for domain in self.cors_domains
                },
            )
        # http://docs.aiohttp.org/en/stable/faq.html#where-do-i-put-my-database-connection-so-handlers-can-access-it
        self.app["exit_stack"] = AsyncExitStack()
        await self.app["exit_stack"].__aenter__()
        self.app.on_shutdown.append(self.on_shutdown)
        self.app["multicomm_contexts"] = {"self": self}
        self.app["multicomm_routes"] = {}
        self.app["sources"] = {}
        self.app["source_contexts"] = {}
        self.app["source_repos_iterkeys"] = {}
        self.app.update(kwargs)
        self.routes = [
            # HTTP Service specific APIs
            ("POST", "/service/upload/{filepath:.+}", self.service_upload),
            # DFFML APIs
            ("GET", "/list/sources", self.list_sources),
            (
                "POST",
                "/configure/source/{source}/{label}",
                self.configure_source,
            ),
            # MutliComm APIs (Data Flow)
            ("POST", "/multicomm/{label}/register", self.multicomm_register),
            # Source APIs
            ("GET", "/source/{label}/repo/{key}", self.source_repo),
            ("POST", "/source/{label}/update/{key}", self.source_update),
            ("GET", "/source/{label}/repos/{chunk_size}", self.source_repos),
            (
                "GET",
                "/source/{label}/repos/{iterkey}/{chunk_size}",
                self.source_repos_iter,
            ),
            # TODO route to delete iterkey before iteration has completed
        ]
        for route in self.routes:
            route = self.app.router.add_route(*route)
            # Add cors to all routes
            if self.cors_domains:
                self.cors.add(route)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
