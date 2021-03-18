import os
import io
import aiohttp
import asyncio
import pathlib
import tempfile
from unittest.mock import patch
from contextlib import asynccontextmanager, ExitStack, AsyncExitStack
from typing import AsyncIterator, Dict

from dffml import DataFlow
from dffml.base import config
from dffml.record import Record
from dffml.df.base import BaseConfig, op
from dffml.operation.output import GetSingle
from dffml.util.entrypoint import EntrypointNotFound
from dffml.model.model import ModelContext, Model
from dffml.model.accuracy import Accuracy
from dffml.feature import Feature
from dffml.source.source import Sources
from dffml.source.csv import CSVSourceConfig
from dffml.util.cli.arg import parse_unknown
from dffml.util.entrypoint import entrypoint
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature.feature import Feature, Features

from dffml_service_http.routes import (
    OK,
    SOURCE_NOT_LOADED,
    MODEL_NOT_LOADED,
    MODEL_NO_SOURCES,
    HTTPChannelConfig,
    DISALLOW_CACHING,
)
from dffml_service_http.util.testing import (
    ServerRunner,
    ServerException,
    TestRoutesRunning,
    FakeModel,
    FakeModelConfig,
)

from .dataflow import (
    HELLO_BLANK_DATAFLOW,
    HELLO_WORLD_DATAFLOW,
    formatter,
    remap,
)


def model_load(loading=None):
    if loading:
        return FakeModel
    return [FakeModel]


class TestRoutesService(TestRoutesRunning, AsyncTestCase):
    async def test_not_found_handler(self):
        with self.assertRaisesRegex(ServerException, "Not Found"):
            async with self.get("/non-existant"):
                pass  # pramga: no cov

    def set_no_cache_do_not_set_any_headers(self, response):
        pass

    async def test_check_allow_caching_header_not_found(self):
        self.cli.set_no_cache = self.set_no_cache_do_not_set_any_headers
        with self.assertRaisesRegex(Exception, "No cache header .* not in"):
            async with self.get("/non-existant"):
                pass  # pramga: no cov

    def set_no_cache_bad_values_for_headers(self, response):
        for header, value in DISALLOW_CACHING.items():
            response.headers[header] = "BAD!"

    async def test_check_allow_caching_header_not_correct(self):
        self.cli.set_no_cache = self.set_no_cache_bad_values_for_headers
        with self.assertRaisesRegex(
            Exception, "No cache header .* should have been .* but was"
        ):
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


class TestRoutesServiceFiles(TestRoutesRunning, AsyncTestCase):
    FILES = {
        ("file.csv",): 327,
        ("there.csv",): 23,
        ("down1", "other.csv"): 71,
        ("down1", "down2", "another.csv"): 560,
        ("down1", "down2", "also.csv"): 464,
        ("down1", "down3", "here.csv"): 127,
    }

    async def test_success(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self.cli.upload_dir = tempdir
            # Create files
            pathlib.Path(tempdir, "down1", "down2").mkdir(parents=True)
            pathlib.Path(tempdir, "down1", "down3").mkdir(parents=True)
            for filepath, size in self.FILES.items():
                pathlib.Path(tempdir, *filepath).write_text("A" * size)

            files = {
                "/".join(filepath): size
                for filepath, size in self.FILES.items()
            }

            async with self.get("/service/files") as r:
                response = {r["filename"]: r["size"] for r in await r.json()}
                for filepath, size in files.items():
                    self.assertIn(filepath, response)
                    self.assertEqual(size, response[filepath])

    async def test_not_allowed(self):
        with self.assertRaisesRegex(
            ServerException, "File listing not allowed"
        ):
            async with self.get("/service/files"):
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
        config = await parse_unknown(
            "--source-filename", "dataset.csv", "-source-allowempty"
        )
        async with self.post("/configure/source/csv/salary", json=config) as r:
            self.assertEqual(await r.json(), OK)
            self.assertIn("salary", self.cli.app["sources"])
            self.assertEqual(
                self.cli.app["sources"]["salary"].config,
                CSVSourceConfig(
                    filename=pathlib.Path("dataset.csv"),
                    tag="untagged",
                    key="key",
                    tagcol="tag",
                    allowempty=True,
                ),
            )
            with self.subTest(context="salaryctx"):
                async with self.get("/context/source/salary/salaryctx") as r:
                    self.assertEqual(await r.json(), OK)
                    self.assertIn("salaryctx", self.cli.app["source_contexts"])

    async def test_source_error(self):
        config = await parse_unknown("--source-file", "dataset.csv")
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
            config = await parse_unknown(
                "--model-directory",
                tempdir,
                "--model-features",
                "Years:int:1",
                "Experiance:int:1",
                "--model-predict",
                "Salary:float:1",
            )
            async with self.post(
                "/configure/model/fake/salary", json=config
            ) as r:
                self.assertEqual(await r.json(), OK)
                self.assertIn("salary", self.cli.app["models"])
                self.assertEqual(
                    self.cli.app["models"]["salary"].config,
                    FakeModelConfig(
                        directory=pathlib.Path(tempdir),
                        features=Features(
                            Feature("Years", int, 1),
                            Feature("Experiance", int, 1),
                        ),
                        predict=Feature("Salary", float, 1),
                    ),
                )
                with self.subTest(context="salaryctx"):
                    # Create the context
                    async with self.get(
                        "/context/model/salary/salaryctx"
                    ) as r:
                        self.assertEqual(await r.json(), OK)
                        self.assertIn(
                            "salaryctx", self.cli.app["model_contexts"]
                        )

    async def test_model_config_error(self):
        # Should be directory, not folder
        config = await parse_unknown("--model-directory", "mymodel_dir")
        with patch.object(Model, "load", new=model_load):
            with self.assertRaisesRegex(ServerException, "missing.*features"):
                async with self.post(
                    "/configure/model/fake/salary", json=config
                ):
                    pass  # pramga: no cov

    async def test_model_context_model_not_found(self):
        with self.assertRaisesRegex(
            ServerException, f"salary model not found"
        ):
            async with self.get("/context/model/salary/salaryctx") as r:
                pass  # pramga: no cov

    async def test_not_found(self):
        for check in ["source", "model"]:
            with self.subTest(check=check):
                with self.assertRaisesRegex(
                    ServerException, f"{check} feed face not found"
                ):
                    async with self.post(
                        f"/configure/{check}/feed face/tag", json={}
                    ):
                        pass  # pramga: no cov


class TestRoutesMultiComm(TestRoutesRunning, AsyncTestCase):
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
                "output_mode": "json",
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
                "output_mode": "json",
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

    async def test_immediate_response(self):
        url: str = "/some/url"
        event = asyncio.Event()

        @op()
        async def my_event_setter(trigger: int) -> None:
            event.set()

        # Register the data flow
        await self.cli.register(
            HTTPChannelConfig(
                path=url,
                dataflow=DataFlow.auto(my_event_setter),
                input_mode=f"text:{my_event_setter.op.inputs['trigger'].name}",
                output_mode="json",
                immediate_response={
                    "status": 200,
                    "content_type": "application/json",
                    "data": {"immediate": "response"},
                },
            )
        )
        async with self.post(url, json="trigger") as response:
            self.assertEqual(await response.json(), {"immediate": "response"})
        await asyncio.wait_for(event.wait(), timeout=2)


class TestRoutesSource(TestRoutesRunning, AsyncTestCase):
    async def setUp(self):
        await super().setUp()
        self.slabel: str = "mydataset"
        self.num_records: int = 100
        self.add_memory_source = await self.exit_stack.enter_async_context(
            self._add_memory_source()
        )

    async def test_source_not_found(self):
        with self.assertRaisesRegex(
            ServerException, list(SOURCE_NOT_LOADED.values())[0]
        ):
            async with self.get("/source/non-existant/record/key"):
                pass  # pramga: no cov

    async def test_record(self):
        for i in range(0, self.num_records):
            async with self.get(f"/source/{self.slabel}/record/{i}") as r:
                self.assertEqual(
                    await r.json(), self.source.config.records[i].export()
                )

    async def test_update(self):
        key = "1"
        new_record = Record(key, data={"features": {"by_ten": 10}})
        async with self.post(
            f"/source/{self.slabel}/update/{key}", json=new_record.export()
        ) as r:
            self.assertEqual(await r.json(), OK)
        self.assertEqual((await self.sctx.record(key)).feature("by_ten"), 10)

    def _check_iter_response(self, response):
        self.assertIn("iterkey", response)
        self.assertIn("records", response)
        for key, record in response["records"].items():
            self.assertEqual(
                record, self.source.config.records[int(key)].export()
            )

    async def test_records(self):
        chunk_size = self.num_records
        async with self.get(
            f"/source/{self.slabel}/records/{chunk_size}"
        ) as r:
            response = await r.json()
            self._check_iter_response(response)
            self.assertEqual(response["iterkey"], None)
            got = len(response["records"].values())
            self.assertEqual(
                got,
                self.num_records,
                f"Not all records were received: got {got}, want: {self.num_records}",
            )

    async def test_records_iterkey(self):
        chunk_size = 7
        got_records = {}
        async with self.get(
            f"/source/{self.slabel}/records/{chunk_size}"
        ) as r:
            response = await r.json()
            self._check_iter_response(response)
            iterkey = response["iterkey"]
            self.assertNotEqual(iterkey, None)
            got_records.update(response["records"])
        while iterkey is not None:
            async with self.get(
                f"/source/{self.slabel}/records/{iterkey}/{chunk_size}"
            ) as r:
                response = await r.json()
                self._check_iter_response(response)
                got_records.update(response["records"])
                iterkey = response["iterkey"]
        got = len(got_records.keys())
        self.assertEqual(
            got,
            self.num_records,
            f"Not all records were received: got {got}, want: {self.num_records}",
        )

    async def test_records_iterkey_not_found(self):
        chunk_size = self.num_records
        iterkey = "feedface"
        with self.assertRaisesRegex(ServerException, "iterkey not found"):
            async with self.get(
                f"/source/{self.slabel}/records/{iterkey}/{chunk_size}"
            ) as r:
                pass  # pramga: no cov


class TestModel(TestRoutesRunning, AsyncTestCase):
    async def setUp(self):
        await super().setUp()
        self.mlabel: str = "mymodel"
        self.slabel: str = "mydataset"
        self.num_records: int = 100
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
        for i in range(0, self.num_records):
            self.assertIn(str(i), self.mctx.trained_on)

    async def test_accuracy(self):
        async with self.post(
            f"/model/{self.mlabel}/accuracy", json=[self.slabel]
        ) as r:
            self.assertEqual(
                await r.json(),
                {"accuracy": float(sum(range(0, self.num_records)))},
            )

    async def test_predict(self):
        records: Dict[str, Record] = {
            record.key: record.export() async for record in self.sctx.records()
        }
        async with self.post(
            f"/model/{self.mlabel}/predict/0", json=records
        ) as r:
            i: int = 0
            response = await r.json()
            for key, record_data in response["records"].items():
                record = Record(key, data=record_data)
                self.assertEqual(int(record.key), i)
                self.assertEqual(
                    record.feature("by_ten"),
                    record.prediction("Salary").value / 10,
                )
                self.assertEqual(
                    float(record.key), record.prediction("Salary").confidence
                )
                i += 1
            self.assertEqual(i, self.num_records)

    async def test_predict_chunk_size_unsupported(self):
        records: Dict[str, Record] = {
            record.key: record.export() async for record in self.sctx.records()
        }
        with self.assertRaisesRegex(
            ServerException, "Multiple request iteration not yet supported"
        ):
            async with self.post(
                f"/model/{self.mlabel}/predict/7", json=records
            ) as r:
                pass  # pramga: no cov
