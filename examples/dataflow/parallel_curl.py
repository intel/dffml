r"""FileName,ProjectId,Url
myfile,123,https://example.com/data.json
"""
import os
import sys
import asyncio
import pathlib
from typing import List

import dffml

DEFAULT_OUTPUT_DIRECTORY = "output"


@dffml.config
class BuildCMDConfig:
    token: str = dffml.field(
        "token to use", default=os.environ.get("token", None)
    )
    directory: str = dffml.field(
        "Directory to download to",
        default=os.environ.get("OUTPUT_DIRECTORY", DEFAULT_OUTPUT_DIRECTORY),
    )


@dffml.op(config_cls=BuildCMDConfig,)
def build_cmd(self, project_id: str, filepath: str, url: str) -> List[str]:
    return [
        "curl",
        "-v",
        "--header",
        "Authorizaiton: Bearer " + self.parent.config.token,
        url,
        "--output",
        f"{self.parent.config.directory}/{project_id}_{filepath}",
    ]


# Output of build_cmd() is used to call subprocess_line_by_line()
build_cmd.op.outputs["result"] = dffml.subprocess_line_by_line.op.inputs["cmd"]
# Set inputs to be from CSV column names
build_cmd.op.inputs["project_id"] = dffml.Definition(
    name="ProjectId", primitive="string"
)
build_cmd.op.inputs["filepath"] = dffml.Definition(
    name="FileName", primitive="string"
)
build_cmd.op.inputs["url"] = dffml.Definition(name="Url", primitive="string")


DATAFLOW = dffml.DataFlow(build_cmd, dffml.subprocess_line_by_line)


async def main(filepath):
    r"""
    Install
    -------

    This relies on development features of DFFML

    .. code-block:: console

        $ python -m pip install -U pip setuptools wheel
        $ python -m pip install -U "https://github.com/pdxjohnny/dffml/archive/manifest.zip#egg=dffml"

    Usage
    -----

    Set MAX_DOWNLOADS environment variable to number of curl calls to run at
    once.

    Set OUTPUT_DIRECTORY to directory to hold output files.

    Files will be saved in OUTPUT_DIRECTORY with following pattern

    .. code-block::

        ${OUTPUT_DIRECTORY}/{$PROJECT_ID}_{FILEPATH_FROM_ROW_IN_CSV}

    .. code-block:: console

        $ token=$JWT python -u parallel_curl.py myfile.csv

    Test
    ----

    .. code-block:: console

        $ token=$JWT python -u -m unittest parallel_curl.py
    """
    max_downloads = int(os.environ.get("MAX_DOWNLOADS", "10"))
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
                record_def=build_cmd.op.inputs["url"].name,
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


class TestParallelCurl(unittest.TestCase):
    def test_parallel(self):
        logging.basicConfig(level=logging.DEBUG)
        with tempfile.TemporaryDirectory() as tempdir:
            # CSV in docstring
            csv_path = pathlib.Path(tempdir, "myfile.csv")
            csv_path.write_text(__doc__)
            # Run curl in parallel
            asyncio.run(main(csv_path))
