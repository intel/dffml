import os
import asyncio
import tempfile
from unittest.mock import patch

from dffml.util.asynctestcase import AsyncTestCase

from dffml_service_http.cli import HTTPService

from .common import ServerRunner


class TestCreateTLS(AsyncTestCase):
    async def test_create(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with self.subTest(certs="server"):
                await HTTPService.createtls.server.cli(
                    "-bits",
                    "1024",
                    "-key",
                    os.path.join(tempdir, "server.key"),
                    "-cert",
                    os.path.join(tempdir, "server.pem"),
                )
                self.assertTrue(
                    os.path.isfile(os.path.join(tempdir, "server.key"))
                )
                self.assertTrue(
                    os.path.isfile(os.path.join(tempdir, "server.pem"))
                )

            with self.subTest(certs="client"):
                await HTTPService.createtls.client.cli(
                    "-bits",
                    "1024",
                    "-key",
                    os.path.join(tempdir, "client.key"),
                    "-cert",
                    os.path.join(tempdir, "client.pem"),
                    "-csr",
                    os.path.join(tempdir, "client.csr"),
                    "-server-key",
                    os.path.join(tempdir, "server.key"),
                    "-server-cert",
                    os.path.join(tempdir, "server.pem"),
                )
                self.assertTrue(
                    os.path.isfile(os.path.join(tempdir, "client.key"))
                )
                self.assertTrue(
                    os.path.isfile(os.path.join(tempdir, "client.pem"))
                )
                self.assertTrue(
                    os.path.isfile(os.path.join(tempdir, "client.csr"))
                )


class TestServer(AsyncTestCase):
    async def test_insecure_off_by_default(self):
        self.assertFalse(HTTPService.server().insecure)

    async def test_start_insecure(self):
        async with ServerRunner.patch(HTTPService.server) as tserver:
            await tserver.start(
                HTTPService.server.cli("-port", "0", "-insecure")
            )

    async def test_start(self):
        with tempfile.TemporaryDirectory() as tempdir:
            await HTTPService.createtls.server.cli(
                "-bits",
                "2048",
                "-key",
                os.path.join(tempdir, "server.key"),
                "-cert",
                os.path.join(tempdir, "server.pem"),
            )
            async with ServerRunner.patch(HTTPService.server) as tserver:
                await tserver.start(
                    HTTPService.server.cli(
                        "-port",
                        "0",
                        "-key",
                        os.path.join(tempdir, "server.key"),
                        "-cert",
                        os.path.join(tempdir, "server.pem"),
                    )
                )
