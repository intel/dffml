import sys
import json
import asyncio
from typing import Dict, Any

from dffml.df.base import op
from dffml.df.types import Definition

package = Definition(name="package", primitive="str")
package_version = Definition(name="package_version", primitive="str")
safety_check_number_of_issues = Definition(
    name="safety_check_number_of_issues", primitive="int"
)


@op(
    name="safety_check",
    inputs={"package": package, "version": package_version},
    outputs={"issues": safety_check_number_of_issues},
    conditions=[],
)
async def safety_check(package: str, version: str) -> Dict[str, Any]:
    pinned = f"{package}=={version}"

    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "safety",
        "check",
        "--stdin",
        "--json",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    proc.stdin.write(pinned.encode())
    proc.stdin.write(b"\n")
    proc.stdin.close()

    stdout, _stderr = await proc.communicate()

    issues = json.loads(stdout)

    return {"issues": len(issues)}
