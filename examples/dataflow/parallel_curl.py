r"""FileName,ProjectId,Url
myfile,123,http://localhost:8000/examples/dataflow/parallel_curl.py
"""
import os
import sys
import asyncio
import pathlib
import http.server
from typing import List

import dffml
import aiohttp
import aiofiles

DEFAULT_OUTPUT_DIRECTORY = "output"


@dffml.config
class DownloadFileConfig:
    token: str = dffml.field(
        "token to use", default=os.environ.get("token", None)
    )
    apikey: str = dffml.field(
        "apikey to use", default=os.environ.get("apikey", None)
    )
    directory: str = dffml.field(
        "Directory to download to",
        default=os.environ.get("OUTPUT_DIRECTORY", DEFAULT_OUTPUT_DIRECTORY),
    )
    chunk_size: str = dffml.field(
        "Chunk of bytes to download and write at a time",
        default=os.environ.get("CHUNK_SIZE", 8192),
    )


@dffml.op(
    config_cls=DownloadFileConfig,
    # imp_enter allows us to create instances of objects which are async context
    # managers and assign them to self.parent which is an object of type
    # OperationImplementation which will be alive for the lifetime of the
    # Orchestrator which runs all these operations.
    imp_enter={
        "session": (
            lambda self: aiohttp.ClientSession(
                # Ironic, for proxies
                trust_env=os.environ.get("TRUST_ENV", None),
                headers={
                    "Authorization": "Bearer " + self.config.token,
                    "Apikey": self.config.apikey,
                },
            )
        )
    },
)
async def download_file(
    self, project_id: str, filepath: str, url: str
) -> None:
    """
    Download a file in chunks, write out to a filename in format of

    .. code-block::

        "{self.parent.config.directory}/{project_id}_{filepath}"
    """
    wrote_bytes = 0
    filename = f"{self.parent.config.directory}/{project_id}_{filepath}"
    if pathlib.Path(filename).exists():
        self.logger.debug(f"skipping {url} as {filename} already exists")
        return
    self.logger.debug(f"making request to {url}")
    async with self.parent.session.get(url) as resp:  # skipcq: BAN-B310
        if resp.status != 200:
            raise Exception(f"Got {url} status {resp.status}")
        async with aiofiles.open(filename, mode="wb") as f:
            async for chunk in resp.content.iter_chunked(
                self.parent.config.chunk_size
            ):
                await f.write(chunk)
                wrote_bytes += len(chunk)
                self.logger.debug(
                    f"wrote {wrote_bytes} bytes of {resp.content_length} to {filename}"
                )
    self.logger.debug(f"Finished writing {wrote_bytes} bytes to {filename}")


# Set inputs to be from CSV column names
download_file.op.inputs["project_id"] = dffml.Definition(
    name="ProjectId", primitive="string"
)
download_file.op.inputs["filepath"] = dffml.Definition(
    name="FileName", primitive="string"
)
download_file.op.inputs["url"] = dffml.Definition(
    name="Url", primitive="string"
)


DATAFLOW = dffml.DataFlow(download_file)


async def main(filepath):
    r"""
    Install
    -------

    This relies on development features of DFFML

    .. code-block:: console

        $ python -m pip install -U pip setuptools wheel
        $ python -m pip install -U aiohttp aiofiles httptest "https://github.com/pdxjohnny/dffml/archive/manifest.zip#egg=dffml"

    Usage
    -----

    Set MAX_DOWNLOADS environment variable to number of curl calls to run at
    once.

    Set OUTPUT_DIRECTORY to directory to hold output files.

    Files will be saved in OUTPUT_DIRECTORY with following pattern

    .. code-block::

        ${OUTPUT_DIRECTORY}/{$PROJECT_ID}_{FILEPATH_FROM_ROW_IN_CSV}

    .. code-block:: console

        $ token=$JWT apikey=$apikey python -u parallel_curl.py myfile.csv

    Test
    ----

    .. code-block:: console

        $ token=$JWT apikey=$apikey python -u -m unittest parallel_curl.py
    """
    max_downloads = int(os.environ.get("MAX_DOWNLOADS", "50"))
    output_directory_path = pathlib.Path(
        os.environ.get("OUTPUT_DIRECTORY", DEFAULT_OUTPUT_DIRECTORY)
    )
    if not output_directory_path.is_dir():
        output_directory_path.mkdir()
    # Run dataflow
    async for record in dffml.load(
        dffml.DataFlowPreprocessSource(
            dffml.DataFlowPreprocessSourceConfig(
                source=dffml.CSVSource(filename=filepath, key="Url"),
                dataflow=DATAFLOW,
                features=dffml.Features(
                    dffml.Feature("FileName", str),
                    dffml.Feature("ProjectId", str),
                ),
                record_def=download_file.op.inputs["url"].name,
                no_strict=True,
                orchestrator=dffml.MemoryOrchestrator(max_ctxs=max_downloads),
            )
        )
    ):
        pass


import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(sys.argv[-1]))


import unittest
import tempfile
import httptest


class TestParallelCurl(unittest.TestCase):
    @httptest.Server(
        lambda *args: http.server.SimpleHTTPRequestHandler(
            *args, directory=pathlib.Path(__file__).parents[2]
        )
    )
    def test_parallel(self, ts=httptest.NoServer()):
        logging.basicConfig(level=logging.DEBUG)
        with tempfile.TemporaryDirectory() as tempdir:
            # CSV in docstring
            csv_path = pathlib.Path(tempdir, "myfile.csv")
            csv_path.write_text(
                __doc__.replace("http://localhost:8000/", ts.url())
            )
            # Run curl in parallel
            asyncio.run(main(csv_path))
