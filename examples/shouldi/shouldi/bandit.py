import io
import os
import sys
import json
import asyncio
from typing import Dict, Any


from dffml.df.types import Definition
from dffml.df.base import op

git_repository = Definition(name="git_repository", primitive="Dict[str,str]")
bandit_output = Definition(name="bandit_output", primitive="Dict[str, Any]")


@op(inputs={"repo": git_repository}, outputs={"report": bandit_output})
async def run_bandit(repo: Dict[str, str]) -> Dict[str, Any]:
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "bandit",
        "-r",
        "-f",
        "json",
        repo["directory"],
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    proc.stdin.write(b"\n")
    proc.stdin.close()
    stdout, _stderr = await proc.communicate()
    if len(stdout) == 0:
        raise Exception
    bandit_op = stdout.decode()
    bandit_op = json.loads(bandit_op)
    t_results = bandit_op["results"]
    high_sev_high_conf = 0
    for item in t_results:
        if (
            item["issue_confidence"] == "HIGH"
            and item["issue_severity"] == "HIGH"
        ):
            high_sev_high_conf += 1
    final_result = bandit_op["metrics"]["_totals"]
    final_result["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"] = high_sev_high_conf
    return {"report": final_result}
