import os
import json
import secrets
import inspect
import pathlib
import traceback
import pkg_resources
from functools import wraps
from http import HTTPStatus
from functools import partial
from dataclasses import dataclass
from contextlib import AsyncExitStack
from typing import List, Union, AsyncIterator, Type, NamedTuple, Dict

from aiohttp import web
import aiohttp_cors

from dffml.record import Record
from dffml.df.types import DataFlow, Input
from dffml.df.multicomm import MultiCommInAtomicMode, BaseMultiCommContext
from dffml.df.memory import (
    MemoryOrchestrator,
    MemoryInputSet,
    MemoryInputSetConfig,
    StringInputSetContext,
)
from dffml.base import MissingConfig
from dffml.model import Model
from dffml.source.source import BaseSource, SourcesContext
from dffml.util.entrypoint import EntrypointNotFound, entrypoint

# Serve the javascript API
API_JS_BYTES = pathlib.Path(
    pkg_resources.resource_filename("dffml_service_http", "api.js")
).read_bytes()

# TODO Add test for this
# Bits of randomness in secret tokens
SECRETS_TOKEN_BITS = 384
SECRETS_TOKEN_BYTES = int(SECRETS_TOKEN_BITS / 8)


OK = {"error": None}
SOURCE_NOT_LOADED = {"error": "Source not loaded"}
MODEL_NOT_LOADED = {"error": "Model not loaded"}
MODEL_NO_SOURCES = {"error": "No source context labels given"}
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
    iterkeys will hold the first record within the next iteration and ths
    iterator. The first time around the first record is None, since we haven't
    iterated yet. We do this because if the chunk_size is the same as the number
    of iterations then we'll need to iterate one time more than chunk_size in
    order to hit the StopAsyncIteration exception.
    """

    first: Union[Record, None]
    records: AsyncIterator[Record]


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
    Ensure that the labeled source context requested is loaded. Return the sctx
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


def mctx_route(handler):
    """
    Ensure that the labeled model context requested is loaded. Return the mctx
    if it is loaded and an error otherwise.
    """

    @wraps(handler)
    async def get_mctx(self, request):
        mctx = request.app["model_contexts"].get(
            request.match_info["label"], None
        )
        if mctx is None:
            return web.json_response(
                MODEL_NOT_LOADED, status=HTTPStatus.NOT_FOUND
            )
        return await handler(self, request, mctx)

    return get_mctx


class HTTPChannelConfig(NamedTuple):
    path: str
    presentation: str
    asynchronous: bool
    dataflow: DataFlow

    @classmethod
    def _fromdict(cls, **kwargs):
        kwargs["dataflow"] = DataFlow._fromdict(**kwargs["dataflow"])
        return cls(**kwargs)


@entrypoint("http")
class Routes(BaseMultiCommContext):
    PRESENTATION_OPTIONS = ["json", "blob", "text"]

    async def get_registered_handler(self, request):
        return self.app["multicomm_routes"].get(request.path, None)

    async def multicomm_dataflow(self, config, request):
        # Seed the network with inputs given by caller
        # TODO(p0,security) allowlist of valid definitions to seed (set
        # Input.origin to something other than seed)
        inputs = []
        # If data was sent add those inputs
        if request.method == "POST":
            # Accept a list of input data
            # TODO validate that input data is dict of list of inputs each item
            # has definition and value properties
            for ctx, client_inputs in (await request.json()).items():
                for input_data in client_inputs:
                    if (
                        not input_data["definition"]
                        in config.dataflow.definitions
                    ):
                        return web.json_response(
                            {
                                "error": f"Missing definition for {input_data['definition']} in dataflow"
                            },
                            status=HTTPStatus.NOT_FOUND,
                        )
                inputs.append(
                    MemoryInputSet(
                        MemoryInputSetConfig(
                            ctx=StringInputSetContext(ctx),
                            inputs=[
                                Input(
                                    value=input_data["value"],
                                    definition=config.dataflow.definitions[
                                        input_data["definition"]
                                    ],
                                )
                                for input_data in client_inputs
                            ],
                        )
                    )
                )
        # Run the operation in an orchestrator
        # TODO(dfass) Create the orchestrator on startup of the HTTP API itself
        async with MemoryOrchestrator.basic_config() as orchestrator:
            # TODO(dfass) Create octx on dataflow registration
            async with orchestrator(config.dataflow) as octx:
                results = {
                    str(ctx): result async for ctx, result in octx.run(*inputs)
                }
                # TODO Implement input and presentation stages?
                """
                if config.presentation == "blob":
                    return web.Response(body=results)
                elif config.presentation == "text":
                    return web.Response(text=results)
                else:
                """
                return web.json_response(results)

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
            response = {"error": error.reason}
            if error.text is not None:
                response["error"] = error.text
            return web.json_response(response, status=error.status)
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

    async def service_files(self, request):
        if self.upload_dir is None:
            return web.json_response(
                {"error": "File listing not allowed"},
                status=HTTPStatus.NOT_IMPLEMENTED,
                headers={"Cache-Control": "no-cache"},
            )

        files: List[Dict[str, Any]] = []

        for filepath in pathlib.Path(self.upload_dir).rglob("**/*.*"):
            filename = str(filepath).replace(self.upload_dir + "/", "")
            files.append(
                {"filename": filename, "size": filepath.stat().st_size}
            )

        return web.json_response(files)

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
            self.logger.error(
                f"failed to configure source {source_name}: {error}"
            )
            return web.json_response(
                {"error": str(error)}, status=HTTPStatus.BAD_REQUEST
            )

        # DFFML objects all follow a double context entry pattern
        exit_stack = request.app["exit_stack"]
        source = await exit_stack.enter_async_context(source)
        request.app["sources"][label] = source

        return web.json_response(OK)

    async def context_source(self, request):
        label = request.match_info["label"]
        ctx_label = request.match_info["ctx_label"]

        if not label in request.app["sources"]:
            return web.json_response(
                {"error": f"{label} source not found"},
                status=HTTPStatus.NOT_FOUND,
            )

        # Enter the source context and pass the features
        exit_stack = request.app["exit_stack"]
        source = request.app["sources"][label]
        mctx = await exit_stack.enter_async_context(source())
        request.app["source_contexts"][ctx_label] = mctx

        return web.json_response(OK)

    async def list_models(self, request):
        return web.json_response(
            {
                model.ENTRY_POINT_ORIG_LABEL: model.args({})
                for model in Model.load()
            },
            dumps=partial(json.dumps, cls=JSONEncoder),
        )

    async def configure_model(self, request):
        model_name = request.match_info["model"]
        label = request.match_info["label"]

        config = await request.json()

        try:
            model = Model.load_labeled(f"{label}={model_name}")
        except EntrypointNotFound as error:
            self.logger.error(
                f"/configure/model/ failed to load model: {error}"
            )
            return web.json_response(
                {"error": f"model {model_name} not found"},
                status=HTTPStatus.NOT_FOUND,
            )

        try:
            model = model.withconfig(config)
        except MissingConfig as error:
            self.logger.error(
                f"failed to configure model {model_name}: {error}"
            )
            return web.json_response(
                {"error": str(error)}, status=HTTPStatus.BAD_REQUEST
            )

        # DFFML objects all follow a double context entry pattern
        exit_stack = request.app["exit_stack"]
        model = await exit_stack.enter_async_context(model)
        request.app["models"][label] = model

        return web.json_response(OK)

    async def context_model(self, request):
        label = request.match_info["label"]
        ctx_label = request.match_info["ctx_label"]

        if not label in request.app["models"]:
            return web.json_response(
                {"error": f"{label} model not found"},
                status=HTTPStatus.NOT_FOUND,
            )

        # Enter the model context and pass the features
        exit_stack = request.app["exit_stack"]
        model = request.app["models"][label]
        mctx = await exit_stack.enter_async_context(model())
        request.app["model_contexts"][ctx_label] = mctx

        return web.json_response(OK)

    def register_config(self) -> Type[HTTPChannelConfig]:
        return HTTPChannelConfig

    async def register(self, config: HTTPChannelConfig) -> None:
        if self.mc_atomic:
            raise MultiCommInAtomicMode("No registrations allowed")
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
        try:
            await mcctx.register(config)
        except:
            return web.json_response(
                {"error": "In atomic mode, no registrations allowed"},
                status=HTTPStatus.BAD_REQUEST,
            )
        return web.json_response(OK)

    @sctx_route
    async def source_record(self, request, sctx):
        return web.json_response(
            (await sctx.record(request.match_info["key"])).export()
        )

    @sctx_route
    async def source_update(self, request, sctx):
        await sctx.update(
            Record(request.match_info["key"], data=await request.json())
        )
        return web.json_response(OK)

    async def _iter_records(self, iterkey, chunk_size) -> List[Record]:
        """
        Iterates over a records async generator and returns a list with chunk_size
        or less records in it (if iteration completed). It also returns the
        iterkey, which will be None if iteration completed.
        """
        if not iterkey in self.app["source_records_iterkeys"]:
            raise web.HTTPNotFound(reason="iterkey not found")
        entry = self.app["source_records_iterkeys"][iterkey]
        # Make record_list start with the last record that was retrieved from
        # iteration the last time _iter_records was called. If this is the first
        # time then record_list is an empty list
        record_list = [entry.first] if entry.first is not None else []
        # We need to iterate one more time than chunk_size the first time
        # _iter_records is called so that we return the chunk_size and set
        # entry.first for the subsequent iterations
        iter_until = chunk_size + 1 if not record_list else chunk_size
        for i in range(0, iter_until):
            try:
                # On last iteration make the record the first record in the next
                # iteration
                if i == (iter_until - 1):
                    entry.first = await entry.records.__anext__()
                else:
                    record_list.append(await entry.records.__anext__())
            except StopAsyncIteration:
                # If we're done iterating over records and can remove the
                # reference to the iterator from iterkeys
                del self.app["source_records_iterkeys"][iterkey]
                iterkey = None
                break
        return iterkey, record_list

    @sctx_route
    async def source_records(self, request, sctx):
        iterkey = secrets.token_hex(nbytes=SECRETS_TOKEN_BYTES)
        # TODO Add test that iterkey is removed on last iteration
        self.app["source_records_iterkeys"][iterkey] = IterkeyEntry(
            first=None, records=sctx.records()
        )
        iterkey, records = await self._iter_records(
            iterkey, int(request.match_info["chunk_size"])
        )
        return web.json_response(
            {
                "iterkey": iterkey,
                "records": {record.key: record.export() for record in records},
            }
        )

    @sctx_route
    async def source_records_iter(self, request, sctx):
        iterkey, records = await self._iter_records(
            request.match_info["iterkey"],
            int(request.match_info["chunk_size"]),
        )
        return web.json_response(
            {
                "iterkey": iterkey,
                "records": {record.key: record.export() for record in records},
            }
        )

    async def get_source_contexts(self, request, sctx_label_list):
        sources_context = SourcesContext([])
        for label in sctx_label_list:
            sctx = request.app["source_contexts"].get(label, None)
            if sctx is None:
                raise web.HTTPNotFound(
                    text=list(SOURCE_NOT_LOADED.values())[0],
                    content_type="application/json",
                )
            sources_context.append(sctx)
        if not sources_context:
            raise web.HTTPBadRequest(
                text=list(MODEL_NO_SOURCES.values())[0],
                content_type="application/json",
            )
        return sources_context

    @mctx_route
    async def model_train(self, request, mctx):
        # Get the list of source context labels to pass to mctx.train
        sctx_label_list = await request.json()
        # Get all the source contexts
        sources = await self.get_source_contexts(request, sctx_label_list)
        # Train the model on the sources
        await mctx.train(sources)
        return web.json_response(OK)

    @mctx_route
    async def model_accuracy(self, request, mctx):
        # Get the list of source context labels to pass to mctx.train
        sctx_label_list = await request.json()
        # Get all the source contexts
        sources = await self.get_source_contexts(request, sctx_label_list)
        # Train the model on the sources
        return web.json_response({"accuracy": await mctx.accuracy(sources)})

    @mctx_route
    async def model_predict(self, request, mctx):
        # TODO Provide an iterkey method for model prediction
        chunk_size = int(request.match_info["chunk_size"])
        if chunk_size != 0:
            return web.json_response(
                {"error": "Multiple request iteration not yet supported"},
                status=HTTPStatus.BAD_REQUEST,
            )
        # Get the records
        records: Dict[str, Record] = {
            key: Record(key, data=record_data)
            for key, record_data in (await request.json()).items()
        }
        # Create an async generator to feed records
        async def record_gen():
            for record in records.values():
                yield record

        # Feed them through prediction
        return web.json_response(
            {
                "iterkey": None,
                "records": {
                    record.key: record.export()
                    async for record in mctx.predict(record_gen())
                },
            }
        )

    async def api_js(self, request):
        return web.Response(
            body=API_JS_BYTES,
            headers={"Content-Type": "application/javascript"},
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
        self.app["source_records_iterkeys"] = {}

        # Instantiate sources if they aren't instantiated yet
        for i, source in enumerate(self.sources):
            if inspect.isclass(source):
                self.sources[i] = source.withconfig(self.extra_config)

        await self.app["exit_stack"].enter_async_context(self.sources)
        self.app["sources"] = {
            source.ENTRY_POINT_LABEL: source for source in self.sources
        }

        mctx = await self.app["exit_stack"].enter_async_context(self.sources())
        self.app["source_contexts"] = {
            source_ctx.parent.ENTRY_POINT_LABEL: source_ctx
            for source_ctx in mctx
        }

        # Instantiate models if they aren't instantiated yet
        for i, model in enumerate(self.models):
            if inspect.isclass(model):
                self.models[i] = model.withconfig(self.extra_config)

        await self.app["exit_stack"].enter_async_context(self.models)
        self.app["models"] = {
            model.ENTRY_POINT_LABEL: model for model in self.models
        }

        mctx = await self.app["exit_stack"].enter_async_context(self.models())
        self.app["model_contexts"] = {
            model_ctx.parent.ENTRY_POINT_LABEL: model_ctx for model_ctx in mctx
        }

        self.app.update(kwargs)
        # Allow no routes other than pre-registered if in atomic mode
        self.routes = (
            []
            if self.mc_atomic
            else [
                # HTTP Service specific APIs
                ("POST", "/service/upload/{filepath:.+}", self.service_upload),
                ("GET", "/service/files", self.service_files),
                # DFFML APIs
                ("GET", "/list/sources", self.list_sources),
                (
                    "POST",
                    "/configure/source/{source}/{label}",
                    self.configure_source,
                ),
                (
                    "GET",
                    "/context/source/{label}/{ctx_label}",
                    self.context_source,
                ),
                ("GET", "/list/models", self.list_models),
                (
                    "POST",
                    "/configure/model/{model}/{label}",
                    self.configure_model,
                ),
                (
                    "GET",
                    "/context/model/{label}/{ctx_label}",
                    self.context_model,
                ),
                # MutliComm APIs (Data Flow)
                (
                    "POST",
                    "/multicomm/{label}/register",
                    self.multicomm_register,
                ),
                # Source APIs
                ("GET", "/source/{label}/record/{key}", self.source_record),
                ("POST", "/source/{label}/update/{key}", self.source_update),
                (
                    "GET",
                    "/source/{label}/records/{chunk_size}",
                    self.source_records,
                ),
                (
                    "GET",
                    "/source/{label}/records/{iterkey}/{chunk_size}",
                    self.source_records_iter,
                ),
                # TODO route to delete iterkey before iteration has completed
                # Model APIs
                ("POST", "/model/{label}/train", self.model_train),
                ("POST", "/model/{label}/accuracy", self.model_accuracy),
                # TODO Provide an iterkey method for model prediction
                (
                    "POST",
                    "/model/{label}/predict/{chunk_size}",
                    self.model_predict,
                ),
            ]
        )
        # Serve api.js
        if self.js:
            self.routes.append(("GET", "/api.js", self.api_js))
        # Add all the routes and make them cors if needed
        for route in self.routes:
            route = self.app.router.add_route(*route)
            # Add cors to all routes
            if self.cors_domains:
                self.cors.add(route)
        # Serve static content
        if self.static:
            self.app.router.add_static("/", self.static)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
