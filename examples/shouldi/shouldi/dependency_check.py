import json
import os
import asyncio
from typing import Dict, Any

from dffml.df.base import op
from dffml.df.types import Definition

package_src_dir = Definition(name="package_src_dir", primitive="str")
dependency_check_output = Definition(
    name="dependency_check_output", primitive="Dict[str, Any]"
)


@op(
    inputs={"pkg": package_src_dir},
    outputs={"report": dependency_check_output},
)
async def run_dependency_check(pkg: str) -> Dict[str, Any]:
    """
    CLI usage: dffml service dev run -log debug shouldi.dependency_check:run_dependency_check -pkg .
    """
    proc = await asyncio.create_subprocess_exec(
        "dependency-check.sh",
        "-f",
        "JSON",
        "-s",
        ".",
        cwd=pkg,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    with open(pkg + "/dependency-check-report.json") as f:
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
