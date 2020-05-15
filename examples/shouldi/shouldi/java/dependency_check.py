import json
import os
import tempfile
from pathlib import Path
import asyncio
from typing import Dict, Any

from dffml import op, Definition

package_src_dir = Definition(name="package_src_dir", primitive="str")
dependency_check_output = Definition(
    name="dependency_check_output", primitive="Dict[str, Any]"
)


class DependencyCheckError(Exception):
    """
    Raised when dependency-check fails
    """


@op(
    inputs={"pkg": package_src_dir},
    outputs={"report": dependency_check_output},
)
async def run_dependency_check(pkg: str) -> Dict[str, Any]:
    """
    CLI usage: dffml service dev run -log debug shouldi.dependency_check:run_dependency_check -pkg .
    """
    with tempfile.TemporaryDirectory() as tempdir:
        if Path(pkg).is_file():
            proc = await asyncio.create_subprocess_exec(
                "dependency-check.sh",
                "-f",
                "JSON",
                "--out",
                os.path.abspath(tempdir),
                "-s",
                pkg,
                cwd=os.path.dirname(pkg),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise DependencyCheckError(stderr.decode())
        else:
            proc = await asyncio.create_subprocess_exec(
                "dependency-check.sh",
                "-f",
                "JSON",
                "--out",
                os.path.abspath(tempdir),
                "-s",
                ".",
                cwd=pkg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise DependencyCheckError(stderr.decode())

        with open(
            os.path.join(
                os.path.abspath(tempdir), "dependency-check-report.json"
            )
        ) as f:
            dependency_check_op = json.loads(f.read())

    for items in dependency_check_op["dependencies"]:
        t_result = items["vulnerabilities"]

    final_report = {}
    score = 0
    for item in t_result:
        final_report["name"] = item["name"]
        final_report["severity"] = item["severity"]
        score += 1
    final_report["total_CVE"] = score

    return {"report": final_report}
