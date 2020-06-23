import sys
import json
import asyncio

from dffml import op
from dffml import Definition


@op
async def run_bandit(pkg: str) -> dict:
    """
    CLI usage: dffml service dev run -log debug shouldi.bandit:run_bandit -pkg .
    """
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "bandit",
        "-r",
        "-f",
        "json",
        pkg,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, _stderr = await proc.communicate()
    if len(stdout) == 0:
        raise Exception
    bandit_op = stdout.decode()
    bandit_op = json.loads(bandit_op)
    t_results = bandit_op["results"]
    final_result = bandit_op["metrics"]["_totals"]
    # Count put number of issues that are high confidence
    for level in ["LOW", "MEDIUM", "HIGH"]:
        high_conf = 0
        for item in t_results:
            if (
                item["issue_confidence"] == "HIGH"
                and item["issue_severity"] == level
            ):
                high_conf += 1
        final_result["CONFIDENCE.HIGH_AND_SEVERITY." + level] = high_conf
    return final_result
