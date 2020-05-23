import shutil
import tempfile
from typing import Dict, Any

import aiohttp

from dffml import op, Definition, Stage

from .safety import package, package_version
from .bandit import package_src_dir


@op(
    # imp_enter allows us to create instances of objects which are async context
    # managers and assign them to self.parent which is an object of type
    # OperationImplementation which will be alive for the lifetime of the
    # Orchestrator which runs all these operations.
    imp_enter={
        "session": (lambda self: aiohttp.ClientSession(trust_env=True))
    },
)
async def pypi_package_json(self, package: str) -> Dict[str, Any]:
    """
    Download the information on the package in JSON format.
    """
    url = f"https://pypi.org/pypi/{package}/json"
    async with self.parent.session.get(url) as resp:  # skipcq: BAN-B310
        package_json = await resp.json()
        return {"response_json": package_json}


@op
async def pypi_latest_package_version(response_json: Dict[str, Any]) -> str:
    """
    Grab the version from the package information.
    """
    return {"version": response_json["info"]["version"]}


@op
async def pypi_package_url(response_json: Dict["str", Any]) -> str:
    """
    Grab the URL of the latest source code release from the package information.
    """
    url_dicts = response_json["urls"]
    for url_dict in url_dicts:
        if (
            url_dict["python_version"] == "source"
            and url_dict["packagetype"] == "sdist"
        ):
            return {"url": url_dict["url"]}


@op(
    imp_enter={
        "session": (lambda self: aiohttp.ClientSession(trust_env=True))
    },
)
async def pypi_package_contents(self, url: str) -> str:
    """
    Download a source code release and extract it to a temporary directory.
    """
    package_src_dir = tempfile.mkdtemp(prefix="pypi-")
    async with self.parent.session.get(url) as resp:
        # Create a temporary file to extract to
        with tempfile.NamedTemporaryFile(
            prefix="pypi-", suffix=".tar.gz"
        ) as package_src_file:
            package_src_file.write(await resp.read())
            shutil.unpack_archive(package_src_file.name, package_src_dir)
            return {"directory": package_src_dir}


@op(stage=Stage.CLEANUP)
async def cleanup_pypi_package(directory: str):
    """
    Remove the directory containing the source code release.
    """
    shutil.rmtree(directory)
