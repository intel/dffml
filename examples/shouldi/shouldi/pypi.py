import aiohttp
from typing import Dict, Any

from dffml.df.types import Definition
from dffml.df.base import op

package = Definition(name="package", primitive="str")
package_version = Definition(name="package_version", primitive="str")


@op(
    inputs={"package": package},
    outputs={"version": package_version},
    imp_enter={
        "session": (lambda self: aiohttp.ClientSession(trust_env=True))
    },
)
async def pypi_latest_package_version(self, package: str) -> Dict[str, Any]:
    url = f"https://pypi.org/pypi/{package}/json"
    async with self.parent.session.get(url) as resp:
        package = await resp.json()
        return {"version": package["info"]["version"]}
