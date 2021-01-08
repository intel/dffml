import ssl
import asyncio
import inspect
import pathlib
import argparse
import subprocess
from typing import List

from aiohttp import web

from dffml.util.cli.cmd import CMD
from dffml import Model, Sources, BaseSource
from dffml.util.cli.parser import list_action
from dffml.util.entrypoint import entrypoint
from dffml.util.asynchelper import AsyncContextManagerList
from dffml.base import config, field

from .routes import Routes


@config
class TLSCMDConfig:
    key: str = field(
        "Path to key file", default="server.key",
    )
    cert: str = field(
        "Path to cert file", default="server.pem",
    )


class TLSCMD(CMD):

    CONFIG = TLSCMDConfig


@config
class CreateTLSServerConfig(TLSCMDConfig):
    bits: int = field(
        "Number of bits to use for key", default=4096,
    )


class CreateTLSServer(TLSCMD):
    """
    Used to generate server key and cert
    """

    CONFIG = CreateTLSServerConfig

    async def run(self):
        subprocess.call(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                f"rsa:{self.bits}",
                "-keyout",
                self.key,
                "-out",
                self.cert,
                "-days",
                "365",
                "-nodes",
                "-sha256",
                "-subj",
                "/C=US/ST=Oregon/L=Portland/O=Feedface/OU=Org/CN=127.0.0.1",
            ]
        )


@config
class CreateTLSClientConfig:
    bits: int = field(
        "Number of bits to use for key", default=4096,
    )
    key: str = field(
        "Path to client key file", default="client.key",
    )
    cert: str = field(
        "Path to client cert file", default="client.pem",
    )
    csr: str = field(
        "Path to client csr file", default="client.csr",
    )
    server_key: str = field(
        "Path to server key file", default="server.key",
    )
    server_cert: str = field(
        "Path to server cert file", default="server.pem",
    )


class CreateTLSClient(CMD):
    """
    Create TLS client key and cert (used to authenticate to HTTP API server).

    curl \\
        --cacert server.pem \\
        --cert client.pem \\
        --key client.key \\
        -vvvvv \\
        https://127.0.0.1:5000/
    """

    CLI_FORMATTER_CLASS = argparse.RawDescriptionHelpFormatter

    CONFIG = CreateTLSClientConfig

    async def run(self):
        subprocess.check_call(
            [
                "openssl",
                "req",
                "-newkey",
                f"rsa:{self.bits}",
                "-keyout",
                self.key,
                "-out",
                self.csr,
                "-nodes",
                "-sha256",
                "-subj",
                "/CN=RealUser",
            ]
        )

        subprocess.check_call(
            [
                "openssl",
                "x509",
                "-req",
                "-in",
                self.csr,
                "-CA",
                self.server_cert,
                "-CAkey",
                self.server_key,
                "-out",
                self.cert,
                "-set_serial",
                "01",
                "-days",
                "365",
            ]
        )


class CreateTLS(TLSCMD):
    """
    Create TLS certificates for server and client authentication
    """

    server = CreateTLSServer
    client = CreateTLSClient


@config
class MultiCommCMDConfig:
    mc_config: str = field(
        "MultiComm config directory", default=None,
    )
    mc_atomic: bool = field(
        "No routes other than dataflows registered at startup",
        action="store_true",
        default=False,
    )


class MultiCommCMD(CMD):

    CONFIG = MultiCommCMDConfig


class RedirectFormatError(Exception):
    """
    Raises when -redirects was not divisible by 3
    """


class ParseRedirectsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        if len(values) % 3 != 0:
            raise RedirectFormatError(
                inspect.cleandoc(
                    r"""
                -redirect usage: METHOD SOURCE_PATH DESTINATION_PATH

                Examples
                --------

                Redirect / to /index.html for GET requests

                    -redirect GET / /index.html

                Redirect / to /index.html for GET requests and /signup to
                /mysignup for POST requests

                    -redirect \
                        GET / /index.html \
                        POST /signup /mysignup
                """
                ).strip()
            )
        setattr(namespace, self.dest, values)


@config
class ServerConfig(TLSCMDConfig, MultiCommCMDConfig):
    port: int = field(
        "Port to bind to", default=8080,
    )
    addr: str = field(
        "Address to bind to", default="127.0.0.1",
    )
    upload_dir: str = field(
        "Directory to store uploaded files in", default=None,
    )
    static: str = field(
        "Directory to serve static content from", default=None,
    )
    js: bool = field(
        "Serve JavaScript API file at /api.js",
        default=False,
        action="store_true",
    )
    insecure: bool = field(
        "Start without TLS encryption", action="store_true", default=False,
    )
    cors_domains: List[str] = field(
        "Domains to allow CORS for (see keys in defaults dict for aiohttp_cors.setup)",
        default_factory=lambda: [],
    )
    allow_caching: bool = field(
        "Allow caching of HTTP responses", action="store_true", default=False,
    )
    models: Model = field(
        "Models configured on start",
        default_factory=lambda: AsyncContextManagerList(),
        action=list_action(AsyncContextManagerList),
        labeled=True,
    )
    sources: Sources = field(
        "Sources configured on start",
        default_factory=lambda: Sources(),
        action=list_action(Sources),
        labeled=True,
    )
    redirect: List[str] = field(
        "list of METHOD SOURCE_PATH DESTINATION_PATH pairs, number of elements must be divisible by 3",
        action=ParseRedirectsAction,
        default_factory=lambda: [],
    )
    portfile: pathlib.Path = field(
        "File to write bound port to when starting. Helpful when port 0 was requeseted to bind to any free port",
        default=None,
    )


class Server(TLSCMD, MultiCommCMD, Routes):
    """
    HTTP server providing access to DFFML APIs
    """

    # Used for testing
    RUN_YIELD_START = False
    RUN_YIELD_FINISH = False
    INSECURE_NO_TLS = False

    CONFIG = ServerConfig

    async def start(self):
        if self.insecure:
            self.site = web.TCPSite(
                self.runner, host=self.addr, port=self.port
            )
        else:
            cert_path = pathlib.Path(self.cert).resolve()
            if not cert_path.is_file():
                raise FileNotFoundError(
                    f"Server cert not found: {cert_path!s}"
                )
            key_path = pathlib.Path(self.key)
            if not key_path.is_file():
                raise FileNotFoundError(f"Server key not found: {key_path!s}")
            ssl_context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH, cafile=str(cert_path)
            )
            ssl_context.load_cert_chain(str(cert_path), str(key_path))
            self.site = web.TCPSite(
                self.runner,
                host=self.addr,
                port=self.port,
                ssl_context=ssl_context,
            )
        await self.site.start()
        self.port = self.site._server.sockets[0].getsockname()[1]
        self.logger.info(f"Serving on {self.addr}:{self.port}")

    async def run(self):
        """
        Binds to port and starts HTTP server
        """
        # Create dictionaries to hold configured sources and models
        await self.setup()
        await self.start()
        # Load
        if self.mc_config is not None:
            # Restore atomic after config is set, allow setting for now
            atomic = self.mc_atomic
            self.mc_atomic = False
            await self.register_directory(self.mc_config)
            self.mc_atomic = atomic
        # Write out port to file
        if self.portfile is not None:
            pathlib.Path(self.portfile).write_text(str(self.port))
        try:
            # If we are testing then RUN_YIELD will be an asyncio.Event
            if self.RUN_YIELD_START is not False:
                await self.RUN_YIELD_START.put(self)
                await self.RUN_YIELD_FINISH.wait()
            else:  # pragma: no cov
                # Wait for ctrl-c
                while True:
                    await asyncio.sleep(60)
        finally:
            await self.app.cleanup()
            await self.site.stop()


@entrypoint("http")
class HTTPService(CMD):
    """
    HTTP interface to access DFFML API.
    """

    server = Server
    createtls = CreateTLS
