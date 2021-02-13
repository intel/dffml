import sys
import json
import asyncio

from dffml import op
from dffml import Definition


@op
async def run_bandit(self, pkg: str) -> dict:
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
    self.logger.debug("Raw scan results: %s", bandit_op)
    bandit_op = json.loads(bandit_op)
    t_results = bandit_op["results"]
    final_result = bandit_op["metrics"]["_totals"]
    # Count put number of issues that are high confidence
    for level in ["LOW", "MEDIUM", "HIGH"]:
        level_key = f"CONFIDENCE.HIGH_AND_SEVERITY.{level}"
        high_conf = 0
        for item in t_results:
            if (
                item["issue_confidence"] == "HIGH"
                and item["issue_severity"] == level
            ):
                high_conf += 1
                # Add this issue to a list of issues found at this severity level
                issue_key = f"{level_key}.issues"
                final_result.setdefault(issue_key, [])
                final_result[issue_key].append(item)
        # Set count of the number of issues we found at both this severity level
        final_result[level_key] = high_conf
    return final_result
