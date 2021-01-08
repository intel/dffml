import os
import json
import asyncio
import secrets
import inspect
import pathlib
import traceback
import urllib.parse
import pkg_resources
from functools import wraps
from http import HTTPStatus
from functools import partial
from dataclasses import dataclass
from contextlib import AsyncExitStack
from typing import List, Union, AsyncIterator, Type, NamedTuple, Dict, Any

import aiohttp_cors
from aiohttp import web


from dffml import Sources, MemorySource
from dffml.record import Record
from dffml.df.types import DataFlow, Input
from dffml.df.multicomm import MultiCommInAtomicMode, BaseMultiCommContext
from dffml.df.memory import (
    MemoryOrchestrator,
    MemoryInputSet,
    MemoryInputSetConfig,
    StringInputSetContext,
)
from dffml.model import Model
from dffml.base import MissingConfig
from dffml.util.data import traverse_get
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

# Headers required to set no-cache for confidential web pages
DISALLOW_CACHING = {
    "Pragma": "no-cache",
    "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate",
    "Expires": "-1",
}

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
    """
    Config for channels.

    Parameters
    ++++++++++
        path : str
            Route in server.
        dataflow : DataFlow
            Flow to which inputs from request to path is forwarded too.
        input_mode : str
            Mode according to which input data is passed to the dataflow,default:"default".
                - "default" :
                    Inputs are expected to be mapping of context to list of input
                        to definition mappings
                        eg:'{
                        "insecure-package":
                            [
                                {
                                    "value":"insecure-package",
                                    "definition":"package"
                                }
                            ]
                        }'
                - "preprocess:definition_name" :
                    Input as whole is treated as value with the given definition.
                    Supported 'preporcess' tags : [json,text,bytes,stream]
        output_mode : str
            Mode according to which output from dataflow is treated.
                - bytes:content_type:OUTPUT_KEYS :
                    OUTPUT_KEYS are . seperated string which is used as keys to traverse the
                    ouput of the flow.
                    eg:
                        `results = {
                            "post_input":
                                {
                                    "hex":b'speak'
                                }
                        }`
                    then bytes:post_input.hex will return b'speak'.
                - text:OUTPUT_KEYS
                - json
                    - output of dataflow (Dict) is passes as json
        immediate_response: Dict[str,Any]
            If provided with a reponse, server responds immediatly with
            it, whilst scheduling to run the dataflow.
            Expected keys:
                - status: HTTP status code for the response
                - content_type: MIME type.If not given, determined
                    from the presence of body/text/json
                - body/text/json: One of this according to content_type
                - headers
            eg:
                {
                    "status": 200,
                    "content_type": "application/json",
                    "data": {"text": "ok"},
                }
    """

    path: str
    dataflow: DataFlow
    output_mode: str = "json"
    asynchronous: bool = False
    input_mode: str = "default"
    forward_headers: str = None
    immediate_response: Dict[str, Any] = None

    @classmethod
    def _fromdict(cls, **kwargs):
        kwargs["dataflow"] = DataFlow._fromdict(**kwargs["dataflow"])
        return cls(**kwargs)


@entrypoint("http")
class Routes(BaseMultiCommContext):
    IO_MODES = ["json", "text", "bytes", "stream"]

    async def get_registered_handler(self, request):
        return self.app["multicomm_routes"].get(request.path, None)

    async def _multicomm_dataflow(self, config, request):
        # Seed the network with inputs given by caller
        # TODO(p0,security) allowlist of valid definitions to seed (set
        # Input.origin to something other than seed)
        inputs = []
        # If data was sent add those inputs
        if request.method == "POST":
            # Accept a list of input data according to config.input_mode
            if config.input_mode == "default":
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
                                ]
                                + (
                                    [
                                        Input(
                                            value=request.headers,
                                            definition=config.dataflow.definitions[
                                                config.forward_headers
                                            ],
                                        )
                                    ]
                                    if config.forward_headers
                                    else []
                                ),
                            )
                        )
                    )
            elif ":" in config.input_mode:
                preprocess_mode, *input_def = config.input_mode.split(":")
                input_def = ":".join(input_def)
                if input_def not in config.dataflow.definitions:
                    return web.json_response(
                        {
                            "error": f"Missing definition for {input_def} in dataflow"
                        },
                        status=HTTPStatus.NOT_FOUND,
                    )

                if preprocess_mode == "json":
                    value = await request.json()
                elif preprocess_mode == "text":
                    value = await request.text()
                elif preprocess_mode == "bytes":
                    value = await request.read()
                elif preprocess_mode == "stream":
                    value = request.content
                else:
                    return web.json_response(
                        {
                            "error": f"preprocess tag must be one of {self.IO_MODES}, got {preprocess_mode}"
                        },
                        status=HTTPStatus.NOT_FOUND,
                    )

                inputs.append(
                    MemoryInputSet(
                        MemoryInputSetConfig(
                            ctx=StringInputSetContext("post_input"),
                            inputs=[
                                Input(
                                    value=value,
                                    definition=config.dataflow.definitions[
                                        input_def
                                    ],
                                )
                            ]
                            + (
                                [
                                    Input(
                                        value=request.headers,
                                        definition=config.dataflow.definitions[
                                            config.forward_headers
                                        ],
                                    )
                                ]
                                if config.forward_headers
                                else []
                            ),
                        )
                    )
                )

            else:
                raise NotImplementedError(
                    "Input modes other than default,preprocess:definition_name  not yet implemented"
                )

        # Run the operation in an orchestrator
        # TODO(dfass) Create the orchestrator on startup of the HTTP API itself
        async with MemoryOrchestrator() as orchestrator:
            # TODO(dfass) Create octx on dataflow registration
            async with orchestrator(config.dataflow) as octx:
                results = {
                    str(ctx): result async for ctx, result in octx.run(*inputs)
                }

                if config.output_mode == "json":
                    return web.json_response(results)

                # content_info is a List[str] ([content_type,output_keys])
                # in case of stream,bytes and string in others
                postprocess_mode, *content_info = config.output_mode.split(":")

                if postprocess_mode == "stream":
                    # stream:text/plain:get_single.beef
                    raise NotImplementedError(
                        "output mode  not yet implemented"
                    )

                elif postprocess_mode == "bytes":
                    content_type, output_keys = content_info
                    output_data = traverse_get(results, output_keys)
                    return web.Response(body=output_data)

                elif postprocess_mode == "text":
                    output_data = traverse_get(results, content_info[0])
                    return web.Response(text=output_data)

                else:
                    return web.json_response(
                        {"error": f"output mode not valid"},
                        status=HTTPStatus.NOT_FOUND,
                    )

    async def multicomm_dataflow(self, config, request):
        if config.immediate_response:
            asyncio.create_task(self._multicomm_dataflow(config, request))
            ir = config.immediate_response
            content_type = None
            if "content_type" in ir:
                content_type = ir["content_type"]
            else:
                if "data" in ir:
                    content_type = "application/json"
                elif "text" in ir:
                    content_type = "text/plain"
                elif "body" in ir:
                    content_type = "application/octet-stream"

            if content_type == "application/json":
                return web.json_response(
                    data={} if not "data" in ir else ir["data"],
                    status=200 if not "status" in ir else ir["status"],
                    headers=None if not "headers" in ir else ir["headers"],
                )
            else:
                return web.Response(
                    body=None if not "body" in ir else ir["body"],
                    text=None if not "text" in ir else ir["text"],
                    status=200 if not "status" in ir else ir["status"],
                    headers=None if not "headers" in ir else ir["headers"],
                    content_type=content_type,
                )
        else:
            return await self._multicomm_dataflow(config, request)

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
        # URL decode match_info values to fix bug where some versions of Python
        # / aiohttp do not decode them
        for key, value in request.match_info.items():
            request.match_info[key] = urllib.parse.unquote(
                value, errors="strict"
            )
        try:
            # HACK This checks if aiohttp's builtin not found handler is going
            # to be called
            # Check if handler is the not found handler
            if (
                "Not Found" in str(handler)
                or "StaticResource" in str(handler)
                or "Method Not Allowed" in str(handler)
            ):
                # Run get_registered_handler to see if we can find the handler
                new_handler = await self.get_registered_handler(request)
                if new_handler is not None:
                    handler = new_handler
            response = await handler(request)
        except web.HTTPException as error:
            response = {"error": error.reason}
            if error.text is not None:
                response["error"] = error.text
            response = web.json_response(response, status=error.status)
        except Exception as error:  #  pragma: no cov
            self.logger.error(
                "ERROR handling %s: %s",
                request,
                traceback.format_exc().strip(),
            )
            response = web.json_response(
                {"error": "Internal Server Error"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        # Disable request caching unless allowed explicitly
        if not self.allow_caching:
            self.set_no_cache(response)
        return response

    def set_no_cache(self, response):
        # Set headers required to set no-cache for confidential web pages
        for header, value in DISALLOW_CACHING.items():
            response.headers[header] = value

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
        if config.output_mode not in self.IO_MODES:
            return web.json_response(
                {
                    "error": f"{config.output_mode!r} is not a valid output_mode option: {self.IO_MODES!r}"
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
        records: Dict[str, Record] = {}
        # Create a source with will provide the records
        async with Sources(
            MemorySource(
                records=[
                    Record(key, data=record_data)
                    for key, record_data in (await request.json()).items()
                ]
            )
        ) as source:
            async with source() as sctx:
                # Feed them through prediction
                return web.json_response(
                    {
                        "iterkey": None,
                        "records": {
                            record.key: record.export()
                            async for record in mctx.predict(sctx)
                        },
                    }
                )

    async def api_js(self, request):
        return web.Response(
            body=API_JS_BYTES,
            headers={"Content-Type": "application/javascript"},
        )

    def mkredirect(self, destination_path):
        async def redirector(request):
            return web.Response(
                status=HTTPStatus.TEMPORARY_REDIRECT,
                headers={"Location": destination_path},
            )

        return redirector

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
        # Redirects
        for method, src, dst in (
            self.redirect[i : i + 3] for i in range(0, len(self.redirect), 3)
        ):
            self.routes.append((method.upper(), src, self.mkredirect(dst)))
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
