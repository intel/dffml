import os
import io
import json
import asyncio
import tempfile
import unittest
from http import HTTPStatus
from unittest.mock import patch
from contextlib import asynccontextmanager, ExitStack, AsyncExitStack
from typing import AsyncIterator, Tuple, Dict, Any, List, NamedTuple

import aiohttp

from dffml.repo import Repo
from dffml.df.base import (
    op,
    BaseConfig,
    BaseInputSetContext,
    BaseOrchestratorContext,
    OperationImplementationContext,
)
from dffml.df.types import Definition, Input, DataFlow, Stage
from dffml.operation.output import GetSingle
from dffml.util.entrypoint import EntrypointNotFound
from dffml.model.model import ModelContext, Model
from dffml.accuracy import Accuracy
from dffml.feature import Features, DefFeature
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.source.source import Sources
from dffml.source.csv import CSVSourceConfig
from dffml.util.data import traverse_get
from dffml.util.cli.arg import parse_unknown
from dffml.util.entrypoint import entry_point
from dffml.util.cli.arg import Arg, parse_unknown
from dffml.util.asynctestcase import AsyncTestCase

from dffml_service_http.cli import Server
from dffml_service_http.routes import (
    OK,
    SOURCE_NOT_LOADED,
    MODEL_NOT_LOADED,
    MODEL_NO_SOURCES,
)

from .common import ServerRunner
from .dataflow import (
    HELLO_BLANK_DATAFLOW,
    HELLO_WORLD_DATAFLOW,
    formatter,
    remap,
)


class ServerException(Exception):
    pass  # pragma: no cov


class FakeModelConfig(NamedTuple):
    directory: str


class FakeModelContext(ModelContext):
    def __init__(self, parent, features):
        super().__init__(parent, features)
        self.trained_on: Dict[str, Repo] = {}

    async def train(self, sources: Sources):
        async for repo in sources.repos():
            self.trained_on[repo.src_url] = repo

    async def accuracy(self, sources: Sources) -> Accuracy:
        accuracy: int = 0
        async for repo in sources.repos():
            accuracy += int(repo.src_url)
        return Accuracy(accuracy)

    async def predict(self, repos: AsyncIterator[Repo]) -> AsyncIterator[Repo]:
        async for repo in repos:
            repo.predicted(repo.feature("by_ten") * 10, float(repo.src_url))
            yield repo


@entry_point("fake")
class FakeModel(Model):

    CONTEXT = FakeModelContext

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, "directory", Arg())
        return args

    @classmethod
    def config(cls, config, *above) -> BaseConfig:
        return FakeModelConfig(
            directory=cls.config_get(config, above, "directory")
        )


def model_load(loading=None):
    if loading:
        return FakeModel
    return [FakeModel]


class TestRoutesRunning:
    async def setUp(self):
        self.exit_stack = AsyncExitStack()
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

    @asynccontextmanager
    async def _add_memory_source(self):
        self.features = Features(DefFeature("by_ten", int, 1))
        async with MemorySource(
            MemorySourceConfig(
                repos=[
                    Repo(str(i), data={"features": {"by_ten": i * 10}})
                    for i in range(0, self.num_repos)
                ]
            )
        ) as source:
            self.source = self.cli.app["sources"][self.slabel] = source
            async with source() as sctx:
                self.sctx = self.cli.app["source_contexts"][self.slabel] = sctx
                yield

    @asynccontextmanager
    async def _add_fake_model(self):
        async with FakeModel(BaseConfig()) as model:
            self.model = self.cli.app["models"][self.mlabel] = model
            async with model(self.features) as mctx:
                self.mctx = self.cli.app["model_contexts"][self.mlabel] = mctx
                yield


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

    async def test_models(self):
        with patch.object(Model, "load", new=model_load):
            async with self.get("/list/models") as r:
                body = await r.json()
                self.assertIn("fake", body)


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
            with self.subTest(context="salaryctx"):
                async with self.get("/context/source/salary/salaryctx") as r:
                    self.assertEqual(await r.json(), OK)
                    self.assertIn("salaryctx", self.cli.app["source_contexts"])

    async def test_source_error(self):
        config = parse_unknown("--source-file", "dataset.csv")
        with self.assertRaisesRegex(ServerException, "missing.*filename"):
            async with self.post("/configure/source/csv/salary", json=config):
                pass  # pramga: no cov

    async def test_source_context_source_not_found(self):
        with self.assertRaisesRegex(
            ServerException, f"salary source not found"
        ):
            async with self.get("/context/source/salary/salaryctx") as r:
                pass  # pramga: no cov

    async def test_model(self):
        with tempfile.TemporaryDirectory() as tempdir, patch.object(
            Model, "load", new=model_load
        ):
            config = parse_unknown("--model-directory", tempdir)
            async with self.post(
                "/configure/model/fake/salary", json=config
            ) as r:
                self.assertEqual(await r.json(), OK)
                self.assertIn("salary", self.cli.app["models"])
                self.assertEqual(
                    self.cli.app["models"]["salary"].config,
                    FakeModelConfig(directory=tempdir),
                )
                with self.subTest(context="salaryctx"):
                    # Define the features
                    features = Features(
                        DefFeature("Years", int, 1),
                        DefFeature("Experiance", int, 1),
                    )
                    exported_features = features.export()
                    # Check that we can send shorthand version of feature_def
                    for name, feature_def in exported_features.items():
                        del feature_def["name"]
                    # Create the context
                    async with self.post(
                        "/context/model/salary/salaryctx",
                        json=exported_features,
                    ) as r:
                        self.assertEqual(await r.json(), OK)
                        self.assertIn(
                            "salaryctx", self.cli.app["model_contexts"]
                        )
                        self.assertEqual(
                            self.cli.app["model_contexts"][
                                "salaryctx"
                            ].features.export(),
                            features.export(),
                        )

    async def test_model_bad_features(self):
        with tempfile.TemporaryDirectory() as tempdir, patch.object(
            Model, "load", new=model_load
        ):
            config = parse_unknown("--model-directory", tempdir)
            async with self.post(
                "/configure/model/fake/salary", json=config
            ) as r:
                self.assertEqual(await r.json(), OK)
                with self.assertRaisesRegex(
                    ServerException, "Incorrect format for features"
                ):
                    async with self.post(
                        "/context/model/salary/salaryctx", json=[]
                    ) as r:
                        pass  # pramga: no cov

    async def test_model_config_error(self):
        # Should be directory, not folder
        config = parse_unknown("--model-folder", "mymodel_dir")
        with patch.object(Model, "load", new=model_load):
            with self.assertRaisesRegex(ServerException, "missing.*directory"):
                async with self.post(
                    "/configure/model/fake/salary", json=config
                ):
                    pass  # pramga: no cov

    async def test_model_context_model_not_found(self):
        with self.assertRaisesRegex(
            ServerException, f"salary model not found"
        ):
            features = Features()
            async with self.post(
                "/context/model/salary/salaryctx", json=features.export()
            ) as r:
                pass  # pramga: no cov

    async def test_not_found(self):
        for check in ["source", "model"]:
            with self.subTest(check=check):
                with self.assertRaisesRegex(
                    ServerException, f"{check} feed face not found"
                ):
                    async with self.post(
                        f"/configure/{check}/feed face/label", json={}
                    ):
                        pass  # pramga: no cov


class TestRoutesMultiComm(TestRoutesRunning, AsyncTestCase):
    OPIMPS = {"formatter": formatter, "get_single": GetSingle, "remap": remap}

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
                "presentation": "json",
                "asynchronous": False,
                "dataflow": HELLO_WORLD_DATAFLOW.export(),
            },
        ) as r:
            self.assertEqual(await r.json(), OK)
        # Test the URL now does exist
        async with self.get(url) as response:
            self.assertEqual(
                {"response": message},
                list((await response.json()).values())[0],
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
                "presentation": "json",
                "asynchronous": False,
                "dataflow": HELLO_BLANK_DATAFLOW.export(),
            },
        ) as r:
            self.assertEqual(await r.json(), OK)
        # Test the URL now does exist (and send data for formatting)
        async with self.post(
            url,
            json={
                "Feedface": [
                    {
                        "value": "Feedface",
                        "definition": formatter.op.inputs["data"].name,
                    }
                ]
            },
        ) as response:
            self.assertEqual(
                {"Feedface": {"response": message}}, await response.json()
            )


class TestRoutesSource(TestRoutesRunning, AsyncTestCase):
    async def setUp(self):
        await super().setUp()
        self.slabel: str = "mydataset"
        self.num_repos: int = 100
        self.add_memory_source = await self.exit_stack.enter_async_context(
            self._add_memory_source()
        )

    async def test_source_not_found(self):
        with self.assertRaisesRegex(
            ServerException, list(SOURCE_NOT_LOADED.values())[0]
        ):
            async with self.get("/source/non-existant/repo/key"):
                pass  # pramga: no cov

    async def test_repo(self):
        for i in range(0, self.num_repos):
            async with self.get(f"/source/{self.slabel}/repo/{i}") as r:
                self.assertEqual(
                    await r.json(), self.source.config.repos[i].export()
                )

    async def test_update(self):
        key = "1"
        new_repo = Repo(key, data={"features": {"by_ten": 10}})
        async with self.post(
            f"/source/{self.slabel}/update/{key}", json=new_repo.export()
        ) as r:
            self.assertEqual(await r.json(), OK)
        self.assertEqual((await self.sctx.repo(key)).feature("by_ten"), 10)

    def _check_iter_response(self, response):
        self.assertIn("iterkey", response)
        self.assertIn("repos", response)
        for src_url, repo in response["repos"].items():
            self.assertEqual(
                repo, self.source.config.repos[int(src_url)].export()
            )

    async def test_repos(self):
        chunk_size = self.num_repos
        async with self.get(f"/source/{self.slabel}/repos/{chunk_size}") as r:
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
        async with self.get(f"/source/{self.slabel}/repos/{chunk_size}") as r:
            response = await r.json()
            self._check_iter_response(response)
            iterkey = response["iterkey"]
            self.assertNotEqual(iterkey, None)
            got_repos.update(response["repos"])
        while iterkey is not None:
            async with self.get(
                f"/source/{self.slabel}/repos/{iterkey}/{chunk_size}"
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
                f"/source/{self.slabel}/repos/{iterkey}/{chunk_size}"
            ) as r:
                pass  # pramga: no cov


class TestModel(TestRoutesRunning, AsyncTestCase):
    async def setUp(self):
        await super().setUp()
        self.mlabel: str = "mymodel"
        self.slabel: str = "mydataset"
        self.num_repos: int = 100
        self.add_memory_source = await self.exit_stack.enter_async_context(
            self._add_memory_source()
        )
        self.add_fake_model = await self.exit_stack.enter_async_context(
            self._add_fake_model()
        )

    async def test_model_not_found(self):
        with self.assertRaisesRegex(
            ServerException, list(MODEL_NOT_LOADED.values())[0]
        ):
            async with self.post(f"/model/non-existant/accuracy", json=[]):
                pass  # pramga: no cov

    async def test_no_sources(self):
        for method in ["train", "accuracy"]:
            with self.subTest(method=method):
                with self.assertRaisesRegex(
                    ServerException, list(MODEL_NO_SOURCES.values())[0]
                ):
                    async with self.post(
                        f"/model/{self.mlabel}/{method}", json=[]
                    ):
                        pass  # pramga: no cov

    async def test_source_not_found(self):
        for method in ["train", "accuracy"]:
            with self.subTest(method=method):
                with self.assertRaisesRegex(
                    ServerException, list(SOURCE_NOT_LOADED.values())[0]
                ):
                    async with self.post(
                        f"/model/{self.mlabel}/train", json=["non-existant"]
                    ):
                        pass  # pramga: no cov

    async def test_train(self):
        async with self.post(
            f"/model/{self.mlabel}/train", json=[self.slabel]
        ) as r:
            self.assertEqual(await r.json(), OK)
        for i in range(0, self.num_repos):
            self.assertIn(str(i), self.mctx.trained_on)

    async def test_accuracy(self):
        async with self.post(
            f"/model/{self.mlabel}/accuracy", json=[self.slabel]
        ) as r:
            self.assertEqual(
                await r.json(),
                {"accuracy": float(sum(range(0, self.num_repos)))},
            )

    async def test_predict(self):
        repos: Dict[str, Repo] = {
            repo.src_url: repo.export() async for repo in self.sctx.repos()
        }
        async with self.post(
            f"/model/{self.mlabel}/predict/0", json=repos
        ) as r:
            i: int = 0
            response = await r.json()
            for src_url, repo_data in response["repos"].items():
                repo = Repo(src_url, data=repo_data)
                self.assertEqual(int(repo.src_url), i)
                self.assertEqual(
                    repo.feature("by_ten"), repo.prediction().value / 10
                )
                self.assertEqual(
                    float(repo.src_url), repo.prediction().confidence
                )
                i += 1
            self.assertEqual(i, self.num_repos)

    async def test_predict_chunk_size_unsupported(self):
        repos: Dict[str, Repo] = {
            repo.src_url: repo.export() async for repo in self.sctx.repos()
        }
        with self.assertRaisesRegex(
            ServerException, "Multiple request iteration not yet supported"
        ):
            async with self.post(
                f"/model/{self.mlabel}/predict/7", json=repos
            ) as r:
                pass  # pramga: no cov
