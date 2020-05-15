import json
import asyncio
from typing import Dict, Any

from dffml import op, Definition

package_src_dir = Definition(name="package_src_dir", primitive="str")
golangci_lint_output = Definition(
    name="golangci_lint_output", primitive="Dict[str, Any]"
)


class GoLangCILintError(Exception):
    """
    Raised when golangci-lint fails
    """


@op(inputs={"pkg": package_src_dir}, outputs={"report": golangci_lint_output})
async def run_golangci_lint(pkg: str) -> Dict[str, Any]:
    """
    CLI usage: dffml service dev run -log debug shouldi.golangci_lint:run_golangci_lint -pkg .
    """
    proc = await asyncio.create_subprocess_exec(
        "golangci-lint",
        "run",
        "--out-format",
        "json",
        "./...",
        cwd=pkg,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if len(stdout) == 0:
        raise GoLangCILintError(stderr)

    golangci_lint_op = stdout.decode()
    issues = json.loads(golangci_lint_op)

    return {"issues": len(issues["Issues"])}
