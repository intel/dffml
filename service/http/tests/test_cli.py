import os
import json
import pathlib
import tempfile
import contextlib
from http import HTTPStatus
from unittest.mock import patch

import aiohttp

from dffml.model.slr import SLRModel
from dffml.source.json import JSONSource
from dffml import Record, Features, Feature, save, train, accuracy
from dffml.util.asynctestcase import AsyncTestCase

from dffml_service_http.cli import HTTPService, RedirectFormatError
from dffml_service_http.util.testing import ServerRunner, ServerException

from .test_routes import TestRoutesMultiComm
from .dataflow import formatter, HELLO_BLANK_DATAFLOW, HELLO_WORLD_DATAFLOW


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

    async def test_portfile(self):
        with tempfile.TemporaryDirectory() as tempdir:
            portfile_path = pathlib.Path(tempdir, "portfile.int")
            async with ServerRunner.patch(HTTPService.server) as tserver:
                cli = await tserver.start(
                    HTTPService.server.cli(
                        "-insecure",
                        "-port",
                        "0",
                        "-portfile",
                        str(portfile_path),
                    )
                )
                self.assertTrue(portfile_path.is_file())
                self.assertEqual(cli.port, int(portfile_path.read_text()))

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
                        "output_mode": "json",
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
                        "output_mode": "json",
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

    async def test_models(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # Model the HTTP API will pre-load
            model = SLRModel(
                features=Features(Feature("f1", float, 1)),
                predict=Feature("ans", int, 1),
                directory=tempdir,
            )

            # y = m * x + b for equation SLR is solving for
            m = 5
            b = 3

            # Train the model
            await train(
                model, *[{"f1": x, "ans": m * x + b} for x in range(0, 10)]
            )

            await accuracy(
                model, *[{"f1": x, "ans": m * x + b} for x in range(10, 20)]
            )

            async with ServerRunner.patch(HTTPService.server) as tserver:
                cli = await tserver.start(
                    HTTPService.server.cli(
                        "-insecure",
                        "-port",
                        "0",
                        "-models",
                        "mymodel=slr",
                        "-model-mymodel-directory",
                        tempdir,
                        "-model-mymodel-features",
                        "f1:float:1",
                        "-model-mymodel-predict",
                        "ans:int:1",
                    )
                )
                async with self.post(
                    cli,
                    f"/model/mymodel/predict/0",
                    json={
                        f"record_{x}": {"features": {"f1": x}}
                        for x in range(20, 30)
                    },
                ) as response:
                    response = await response.json()
                    records = response["records"]
                    self.assertEqual(len(records), 10)
                    for record in records.values():
                        should_be = m * record["features"]["f1"] + b
                        prediction = record["prediction"]["ans"]["value"]
                        percent_error = abs(should_be - prediction) / should_be
                        self.assertLess(percent_error, 0.2)

    async def test_sources(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # Source the HTTP API will pre-load
            source = JSONSource(
                filename=pathlib.Path(tempdir, "source.json"),
                allowempty=True,
                readwrite=True,
            )

            # Record the source will have in it
            myrecord = Record("myrecord", data={"features": {"f1": 0}})
            await save(source, myrecord)

            async with ServerRunner.patch(HTTPService.server) as tserver:
                cli = await tserver.start(
                    HTTPService.server.cli(
                        "-insecure",
                        "-port",
                        "0",
                        "-sources",
                        "mysource=json",
                        "-source-mysource-filename",
                        str(source.config.filename),
                    )
                )
                async with self.get(
                    cli, "/source/mysource/record/myrecord"
                ) as r:
                    self.assertEqual(await r.json(), myrecord.export())

    async def test_redirect_format_error(self):
        with self.assertRaises(RedirectFormatError):
            async with ServerRunner.patch(HTTPService.server) as tserver:
                await tserver.start(
                    # Missing METHOD
                    HTTPService.server.cli(
                        "-insecure",
                        "-port",
                        "0",
                        "-redirect",
                        "/",
                        "/index.html",
                    )
                )

    async def test_redirect(self):
        with tempfile.TemporaryDirectory() as tempdir:
            pathlib.Path(tempdir, "index.html").write_text("Hello World")
            pathlib.Path(tempdir, "mysignup").write_text("MySignUp")
            async with ServerRunner.patch(HTTPService.server) as tserver:
                cli = await tserver.start(
                    HTTPService.server.cli(
                        "-insecure",
                        "-port",
                        "0",
                        "-static",
                        tempdir,
                        "-redirect",
                        "GET",
                        "/",
                        "/index.html",
                        "GET",
                        "/signup",
                        "/mysignup",
                    )
                )
                async with self.get(cli, "/") as r:
                    self.assertEqual(await r.text(), "Hello World")
                async with self.get(cli, "/signup") as r:
                    self.assertEqual(await r.text(), "MySignUp")
