import os
import io
import json
import asyncio
import tempfile
from http import HTTPStatus
from unittest.mock import patch
from contextlib import asynccontextmanager, ExitStack

import aiohttp

from dffml.repo import Repo
from dffml.df.base import op
from dffml.df.types import Definition
from dffml.operation.output import GetSingle
from dffml.util.entrypoint import EntrypointNotFound
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.source.csv import CSVSourceConfig
from dffml.util.cli.arg import parse_unknown
from dffml.util.asynctestcase import AsyncTestCase

from dffml_service_http.cli import Server
from dffml_service_http.routes import OK, SOURCE_NOT_LOADED

from .common import ServerRunner


class ServerException(Exception):
    pass  # pragma: no cov


class TestRoutesRunning:
    async def setUp(self):
        self._tserver = ServerRunner.patch(Server)
        self.tserver = await self._tserver.__aenter__()
        self.cli = Server(port=0, insecure=True)
        await self.tserver.start(self.cli.run())
        # Set up client
        self._client = aiohttp.ClientSession()
        self.session = await self._client.__aenter__()

    async def tearDown(self):
        await self._client.__aexit__(None, None, None)
        await self._tserver.__aexit__(None, None, None)

    @property
    def url(self):
        return f"http://{self.cli.addr}:{self.cli.port}"

    @asynccontextmanager
    async def get(self, path):
        async with self.session.get(self.url + path) as r:
            if r.status != HTTPStatus.OK:
                raise ServerException((await r.json())["error"])
            yield r

    @asynccontextmanager
    async def post(self, path, *args, **kwargs):
        async with self.session.post(self.url + path, *args, **kwargs) as r:
            if r.status != HTTPStatus.OK:
                raise ServerException((await r.json())["error"])
            yield r


class TestRoutesService(TestRoutesRunning, AsyncTestCase):
    async def test_not_found_handler(self):
        with self.assertRaisesRegex(ServerException, "Not Found"):
            async with self.get("/non-existant"):
                pass  # pramga: no cov


class TestRoutesServiceUpload(TestRoutesRunning, AsyncTestCase):
    async def test_success(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self.cli.upload_dir = tempdir
            contents = b"X,Y\n1,10\n2,20\n3,30\n"
            async with self.post(
                "/service/upload/somefile", data={"file": io.BytesIO(contents)}
            ) as r:
                self.assertEqual(await r.json(), OK)
                self.assertTrue(
                    os.path.isfile(os.path.join(tempdir, "somefile"))
                )
                with open(os.path.join(tempdir, "somefile"), "rb") as check:
                    self.assertTrue(check.read(), contents)

    async def test_not_allowed(self):
        with self.assertRaisesRegex(ServerException, "Uploads not allowed"):
            async with self.post(
                "/service/upload/somefile", data={"file": io.BytesIO(b"nope")}
            ):
                pass  # pramga: no cov

    async def test_path_traversal(self):
        # TODO Test path traversal, aiohttp client keeps changing /path/../ into
        # / before sending the request.
        return

    async def test_missing_file_field(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self.cli.upload_dir = tempdir
            with self.assertRaisesRegex(
                ServerException, "Missing 'file' field"
            ):
                async with self.post(
                    "/service/upload/somefile",
                    data={"nope": io.BytesIO(b"nope")},
                ) as r:
                    pass  # pramga: no cov


class TestRoutesList(TestRoutesRunning, AsyncTestCase):
    async def test_sources(self):
        async with self.get("/list/sources") as r:
            body = await r.json()
            self.assertIn("csv", body)
            self.assertIn("json", body)
            self.assertIn("memory", body)


class TestRoutesConfigure(TestRoutesRunning, AsyncTestCase):
    async def test_source(self):
        config = parse_unknown(
            "--source-filename", "dataset.csv", "--source-readonly"
        )
        async with self.post("/configure/source/csv/salary", json=config) as r:
            self.assertEqual(await r.json(), OK)
            self.assertIn("salary", self.cli.app["sources"])
            self.assertEqual(
                self.cli.app["sources"]["salary"].config,
                CSVSourceConfig(
                    filename="dataset.csv",
                    label="unlabeled",
                    readonly=True,
                    key="src_url",
                    label_column="label",
                ),
            )

    async def test_source_error(self):
        config = parse_unknown("--source-file", "dataset.csv")
        with self.assertRaisesRegex(ServerException, "missing.*filename"):
            async with self.post("/configure/source/csv/salary", json=config):
                pass  # pramga: no cov

    async def test_source_not_found(self):
        with self.assertRaisesRegex(
            ServerException, "source feed face not found"
        ):
            async with self.post(
                "/configure/source/feed face/salary", json={}
            ):
                pass  # pramga: no cov


@op(
    inputs={
        "data": Definition(name="format_data", primitive="string"),
        "formatting": Definition(name="format_string", primitive="string"),
    },
    outputs={"string": Definition(name="message", primitive="string")},
)
def formatter(formatting: str, data: str):
    return {"string": formatting.format(data)}


class TestRoutesMultiComm(TestRoutesRunning, AsyncTestCase):
    OPIMPS = {"formatter": formatter, "get_single": GetSingle}

    @classmethod
    def patch_operation_implementation_load(cls, loading):
        try:
            return cls.OPIMPS[loading].imp
        except KeyError as error:
            raise EntrypointNotFound(
                f"{loading} not found in {list(cls.OPIMPS.keys())}"
            ) from error

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._exit_stack = ExitStack()
        cls.exit_stack = cls._exit_stack.__enter__()
        cls.exit_stack.enter_context(
            patch(
                "dffml.df.base.OperationImplementation.load",
                new=cls.patch_operation_implementation_load,
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._exit_stack.__exit__(None, None, None)

    async def test_no_post(self):
        url: str = "/some/url"
        message: str = "Hello World"
        # Test that URL does not exist
        with self.assertRaisesRegex(ServerException, "Not Found"):
            async with self.get(url):
                pass  # pramga: no cov
        # Register the data flow
        async with self.post(
            f"/multicomm/self/register",
            json={
                "path": url,
                "asynchronous": False,
                "dataflow": {
                    "operations": {
                        "hello_blank": formatter.op.export(),
                        "get_formatted_message": GetSingle.op.export(),
                    },
                    # TODO use configs for format instead of seed
                    "configs": {"say.hello": {"format": "Hello {}"}},
                    "seed": [
                        {
                            "value": "World",
                            "definition": formatter.op.inputs["data"].export(),
                        },
                        {
                            "value": "Hello {}",
                            "definition": formatter.op.inputs[
                                "formatting"
                            ].export(),
                        },
                        {
                            "value": [formatter.op.outputs["string"].name],
                            "definition": GetSingle.op.inputs["spec"].export(),
                        },
                    ],
                    "remap": {
                        "response": [
                            GetSingle.op.name,
                            formatter.op.outputs["string"].name,
                        ]
                    },
                },
            },
        ) as r:
            self.assertEqual(await r.json(), OK)
        # Test the URL now does exist
        async with self.get(url) as response:
            self.assertEqual(
                json.dumps({"response": message}), await response.text()
            )

    async def test_post(self):
        url: str = "/some/url"
        message: str = "Hello Feedface"
        # Test that URL does not exist
        with self.assertRaisesRegex(ServerException, "Not Found"):
            async with self.get(url):
                pass  # pramga: no cov
        # Register the data flow
        async with self.post(
            f"/multicomm/self/register",
            json={
                "path": url,
                "asynchronous": False,
                "dataflow": {
                    "operations": {
                        "hello_blank": formatter.op.export(),
                        "get_formatted_message": GetSingle.op.export(),
                    },
                    # TODO use configs for format instead of seed
                    "configs": {"say.hello": {"format": "Hello {}"}},
                    "seed": [
                        {
                            "value": "Hello {}",
                            "definition": formatter.op.inputs[
                                "formatting"
                            ].export(),
                        },
                        {
                            "value": [formatter.op.outputs["string"].name],
                            "definition": GetSingle.op.inputs["spec"].export(),
                        },
                    ],
                    "remap": {
                        "response": [
                            GetSingle.op.name,
                            formatter.op.outputs["string"].name,
                        ]
                    },
                },
            },
        ) as r:
            self.assertEqual(await r.json(), OK)
        # Test the URL now does exist (and send data for formatting)
        async with self.post(
            url,
            json=[
                {
                    "value": "Feedface",
                    "definition": formatter.op.inputs["data"].export(),
                }
            ],
        ) as response:
            self.assertEqual(
                json.dumps({"response": message}), await response.text()
            )


class TestRoutesSource(TestRoutesRunning, AsyncTestCase):
    @asynccontextmanager
    async def _add_memory_source(self):

        async with MemorySource(
            MemorySourceConfig(
                repos=[
                    Repo(str(i), data={"features": {"by_ten": i * 10}})
                    for i in range(0, self.num_repos)
                ]
            )
        ) as source:
            self.source = self.cli.app["sources"][self.label] = source
            async with source() as sctx:
                self.sctx = self.cli.app["source_contexts"][self.label] = sctx
                yield

    async def setUp(self):
        await super().setUp()
        self.label: str = "mydataset"
        self.num_repos: int = 100
        self.add_memory_source = self._add_memory_source()
        await self.add_memory_source.__aenter__()

    async def tearDown(self):
        await super().tearDown()
        await self.add_memory_source.__aexit__(None, None, None)

    async def test_source_not_found(self):
        with self.assertRaisesRegex(
            ServerException, list(SOURCE_NOT_LOADED.values())[0]
        ):
            async with self.get("/source/non-existant/repo/key"):
                pass  # pramga: no cov

    async def test_repo(self):
        for i in range(0, self.num_repos):
            async with self.get(f"/source/{self.label}/repo/{i}") as r:
                self.assertEqual(
                    await r.json(), self.source.config.repos[i].dict()
                )

    async def test_update(self):
        key = "1"
        new_repo = Repo(key, data={"features": {"by_ten": 10}})
        async with self.post(
            f"/source/{self.label}/update/{key}", json=new_repo.dict()
        ) as r:
            self.assertEqual(await r.json(), OK)
        self.assertEqual((await self.sctx.repo(key)).feature("by_ten"), 10)

    def _check_iter_response(self, response):
        self.assertIn("iterkey", response)
        self.assertIn("repos", response)
        for src_url, repo in response["repos"].items():
            self.assertEqual(
                repo, self.source.config.repos[int(src_url)].dict()
            )

    async def test_repos(self):
        chunk_size = self.num_repos
        async with self.get(f"/source/{self.label}/repos/{chunk_size}") as r:
            response = await r.json()
            self._check_iter_response(response)
            self.assertEqual(response["iterkey"], None)
            got = len(response["repos"].values())
            self.assertEqual(
                got,
                self.num_repos,
                f"Not all repos were received: got {got}, want: {self.num_repos}",
            )

    async def test_repos_iterkey(self):
        chunk_size = 7
        got_repos = {}
        async with self.get(f"/source/{self.label}/repos/{chunk_size}") as r:
            response = await r.json()
            self._check_iter_response(response)
            iterkey = response["iterkey"]
            self.assertNotEqual(iterkey, None)
            got_repos.update(response["repos"])
        while iterkey is not None:
            async with self.get(
                f"/source/{self.label}/repos/{iterkey}/{chunk_size}"
            ) as r:
                response = await r.json()
                self._check_iter_response(response)
                got_repos.update(response["repos"])
                iterkey = response["iterkey"]
        got = len(got_repos.keys())
        self.assertEqual(
            got,
            self.num_repos,
            f"Not all repos were received: got {got}, want: {self.num_repos}",
        )

    async def test_repos_iterkey_not_found(self):
        chunk_size = self.num_repos
        iterkey = "feedface"
        with self.assertRaisesRegex(ServerException, "iterkey not found"):
            async with self.get(
                f"/source/{self.label}/repos/{iterkey}/{chunk_size}"
            ) as r:
                pass  # pramga: no cov
