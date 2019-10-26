import os
import ssl
import asyncio
import argparse
import subprocess

from aiohttp import web

from dffml.util.cli.arg import Arg
from dffml.util.cli.cmd import CMD
from dffml.util.entrypoint import entry_point

from .routes import Routes


class TLSCMD(CMD):

    arg_key = Arg("-key", help="Path to key file", default="server.key")
    arg_cert = Arg("-cert", help="Path to cert file", default="server.pem")


class CreateTLSServer(TLSCMD):
    """
    Used to generate server key and cert
    """

    arg_bits = Arg(
        "-bits", help="Number of bits to use for key", default=4096, type=int
    )

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

    arg_bits = Arg(
        "-bits", help="Number of bits to use for key", default=4096, type=int
    )
    arg_key = Arg("-key", help="Path to client key file", default="client.key")
    arg_cert = Arg(
        "-cert", help="Path to client cert file", default="client.pem"
    )
    arg_csr = Arg("-csr", help="Path to client csr file", default="client.csr")
    arg_server_key = Arg(
        "-server-key", help="Path to server key file", default="server.key"
    )
    arg_server_cert = Arg(
        "-server-cert", help="Path to server cert file", default="server.pem"
    )

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


class MultiCommCMD(CMD):

    mc_config = Arg(
        "-mc-config",
        dest="mc_config",
        default=None,
        help="MultiComm config directory",
    )
    mc_atomic = Arg(
        "-mc-atomic",
        dest="mc_atomic",
        action="store_true",
        default=False,
        help="No routes other than dataflows registered at startup",
    )


class Server(TLSCMD, MultiCommCMD, Routes):
    """
    HTTP server providing access to DFFML APIs
    """

    # Used for testing
    RUN_YIELD_START = False
    RUN_YIELD_FINISH = False
    INSECURE_NO_TLS = False

    arg_port = Arg("-port", help="Port to bind to", type=int, default=8080)
    arg_addr = Arg("-addr", help="Address to bind to", default="127.0.0.1")
    arg_upload_dir = Arg(
        "-upload-dir",
        help="Directory to store uploaded files in",
        default=None,
    )
    arg_insecure = Arg(
        "-insecure",
        help="Start without TLS encryption",
        action="store_true",
        default=False,
    )
    arg_cors_domains = Arg(
        "-cors-domains",
        help="Domains to allow CORS for (see keys in defaults dict for aiohttp_cors.setup)",
        nargs="+",
        default=[],
    )

    def __init__(self, *args, **kwargs):
        self._port: int = 0
        self.site = None
        super().__init__(*args, **kwargs)

    @property
    def port(self):
        if self.site is None or self.site._server is None:
            return self._port
        return self.site._server.sockets[0].getsockname()[1]

    @port.setter
    def port(self, value):
        self._port = value

    async def start(self):
        if self.insecure:
            self.site = web.TCPSite(
                self.runner, host=self.addr, port=self.port
            )
        else:
            ssl_context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH, cafile=self.cert
            )
            ssl_context.load_cert_chain(self.cert, self.key)
            self.site = web.TCPSite(
                self.runner,
                host=self.addr,
                port=self.port,
                ssl_context=ssl_context,
            )
        await self.site.start()
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


@entry_point("http")
class HTTPService(CMD):
    """
    HTTP interface to access DFFML API.
    """

    server = Server
    createtls = CreateTLS
