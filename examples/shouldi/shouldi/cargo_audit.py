import json
import asyncio
from typing import Dict, Any

from dffml.df.base import op
from dffml.df.types import Definition

package_src_dir = Definition(name="package_src_dir", primitive="str")
cargo_audit_output = Definition(
    name="golangci_lint_output", primitive="Dict[str, Any]"
)


class Cargo_AuditError(Exception):
    """
    Raised when cargo-audit fails
    """


@op(inputs={"pkg": package_src_dir}, outputs={"report": cargo_audit_output})
async def run_cargo_audit(pkg: str) -> Dict[str, Any]:
    """
    CLI usage: dffml service dev run -log debug shouldi.cargo_audit:run_cargo_audit -pkg .
    """
    proc = await asyncio.create_subprocess_exec(
        "cargo-audit",
        "audit"
        "--json",
        cwd=pkg,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if len(stdout) == 0:
        raise Cargo_AuditError(stderr)

    cargo_audit_op = stdout.decode()
    issues = json.loads(cargo_audit_op)
    result = issues["vulnerabilities"]["count"]

    return {"report": result}
