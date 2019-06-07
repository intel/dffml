import io
import json
import asyncio
from typing import Dict, Any

from dffml.df.types import Definition
from dffml.df.base import op

from .pypi import package, package_version

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
