import aiohttp
import tempfile
import shutil
from typing import Dict, Any

from dffml.df.types import Definition, Stage
from dffml.df.base import op

package = Definition(name="package", primitive="str")
package_json = Definition(name="package_json", primitive="Dict[str, Any]")
package_version = Definition(name="package_version", primitive="str")
package_url = Definition(name="package_url", primitive="str")
package_src_dir = Definition(name="package_src_dir", primitive="str")


@op(
    inputs={"package": package},
    outputs={"response_json": package_json},
    imp_enter={
        "session": (lambda self: aiohttp.ClientSession(trust_env=True))
    },
)
async def pypi_package_json(self, package: str) -> Dict[str, Any]:
    url = f"https://pypi.org/pypi/{package}/json"
    async with self.parent.session.get(url) as resp:
        package_json = await resp.json()
        return {"response_json": package_json}


@op(
    inputs={"response_json": package_json},
    outputs={"version": package_version},
)
async def pypi_latest_package_version(response_json: Dict[str, Any]) -> str:
    return {"version": response_json["info"]["version"]}


@op(inputs={"response_json": package_json}, outputs={"url": package_url})
async def pypi_package_url(response_json: Dict["str", Any]) -> str:
    url_dicts = response_json["urls"]
    for url_dict in url_dicts:
        if (
            url_dict["python_version"] == "source"
            and url_dict["packagetype"] == "sdist"
        ):
            return {"url": url_dict["url"]}


@op(
    inputs={"url": package_url},
    outputs={"directory": package_src_dir},
    imp_enter={
        "session": (lambda self: aiohttp.ClientSession(trust_env=True))
    },
)
async def pypi_package_contents(self, url: str) -> str:
    package_src_dir = tempfile.mkdtemp(prefix="pypi-")
    async with self.parent.session.get(url) as resp:
        if resp.status == 200:
            package_src_file = tempfile.NamedTemporaryFile(
                prefix="pypi-", suffix=".tar.gz"
            )
            package_src_file.write(await resp.read())
            shutil.unpack_archive(package_src_file.name, package_src_dir)
            return {"directory": package_src_dir}


@op(inputs={"directory": package_src_dir}, outputs={}, stage=Stage.CLEANUP)
async def cleanup_pypi_package(directory: str):
    try:
        shutil.rmtree(directory)
    except FileNotFoundError:
        return {"op": "failed"}
    return {}
