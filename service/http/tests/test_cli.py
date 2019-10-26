import os
import json
import pathlib
import asyncio
import tempfile
import contextlib
from http import HTTPStatus
from unittest.mock import patch

import aiohttp

from dffml.util.asynctestcase import AsyncTestCase

from dffml_service_http.cli import HTTPService

from .common import ServerRunner
from .dataflow import formatter, HELLO_BLANK_DATAFLOW, HELLO_WORLD_DATAFLOW
from .test_routes import ServerException, TestRoutesMultiComm


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
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._exit_stack = contextlib.ExitStack()
        cls.exit_stack = cls._exit_stack.__enter__()
        cls.exit_stack.enter_context(
            patch(
                "dffml.df.base.OperationImplementation.load",
                new=TestRoutesMultiComm.patch_operation_implementation_load,
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._exit_stack.__exit__(None, None, None)

    def url(self, cli):
        return f"http://{cli.addr}:{cli.port}"

    @contextlib.asynccontextmanager
    async def get(self, cli, path):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url(cli) + path) as r:
                if r.status != HTTPStatus.OK:
                    raise ServerException((await r.json())["error"])
                yield r

    @contextlib.asynccontextmanager
    async def post(self, cli, path, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url(cli) + path, *args, **kwargs
            ) as r:
                if r.status != HTTPStatus.OK:
                    raise ServerException((await r.json())["error"])
                yield r

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

    async def test_mc_config(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # URLs for endpoints
            hello_world_url: str = "/hello/world"
            hello_blank_url: str = "/hello/blank"
            # Create the required directory structure
            # Create directories for multicomm, dataflow, and dataflow overrides
            pathlib.Path(tempdir, "mc").mkdir()
            pathlib.Path(tempdir, "mc", "http").mkdir()
            pathlib.Path(tempdir, "df").mkdir()
            # TODO split config part of dataflow into seperate directory
            pathlib.Path(tempdir, "config").mkdir()
            # Write out multicomm configs
            pathlib.Path(tempdir, "mc", "http", "hello_world.json").write_text(
                json.dumps(
                    {
                        "path": hello_world_url,
                        "presentation": "json",
                        "asynchronous": False,
                    },
                    sort_keys=True,
                    indent=4,
                )
            )
            pathlib.Path(tempdir, "mc", "http", "hello_blank.json").write_text(
                json.dumps(
                    {
                        "path": hello_blank_url,
                        "presentation": "json",
                        "asynchronous": False,
                    },
                    sort_keys=True,
                    indent=4,
                )
            )
            # Write out dataflow configs
            pathlib.Path(tempdir, "df", "hello_world.json").write_text(
                json.dumps(
                    HELLO_WORLD_DATAFLOW.export(), sort_keys=True, indent=4
                )
            )
            pathlib.Path(tempdir, "df", "hello_blank.json").write_text(
                json.dumps(
                    HELLO_BLANK_DATAFLOW.export(), sort_keys=True, indent=4
                )
            )
            # Start the server
            async with ServerRunner.patch(HTTPService.server) as tserver:
                cli = await tserver.start(
                    HTTPService.server.cli(
                        "-port",
                        "0",
                        "-insecure",
                        "-mc-config",
                        tempdir,
                        "-mc-atomic",
                    )
                )
                self.assertEqual(cli.mc_config, tempdir)
                # Verify routes were registered and preform as expected
                message: str = "Hello World"
                with self.subTest(test=message):
                    # Check that hello world works
                    async with self.get(cli, hello_world_url) as response:
                        self.assertEqual(
                            {"response": message},
                            list((await response.json()).values())[0],
                        )
                # Check that hello blank works
                message: str = "Hello Feedface"
                with self.subTest(test=message):
                    async with self.post(
                        cli,
                        hello_blank_url,
                        json={
                            "Feedface": [
                                {
                                    "value": "Feedface",
                                    "definition": formatter.op.inputs[
                                        "data"
                                    ].name,
                                }
                            ]
                        },
                    ) as response:
                        self.assertEqual(
                            {"Feedface": {"response": message}},
                            await response.json(),
                        )
