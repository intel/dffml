import aiohttp
from typing import Dict, Any

from dffml.df.types import Definition
from dffml.df.base import op

package = Definition(name="package", primitive="str")
package_json = Definition(name="package_json", primitive="Dict[str, Any]")
package_version = Definition(name="package_version", primitive="str")


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
        package = await resp.json()
        return {"response_json": package}

@op(
    inputs={"response_json": package_json},
    output={"version": package_version}
)
async def pypi_latest_package_version(package_json: Dict["str", Any]) -> str:
    return {"version": package_json["info"]["version"]}
