import sys
import json
import asyncio

from dffml import op
from dffml import Definition


@op
async def safety_check(package: str, version: str) -> int:
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

    stdout, _stderr = await proc.communicate(pinned.encode() + b"\n")

    issues = json.loads(stdout)

    return len(issues)
