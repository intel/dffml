import json
import asyncio
from typing import Dict, Any

from dffml.df.base import op
from dffml.df.types import Definition

package_src_dir = Definition(name="package_src_dir", primitive="str")
cargo_audit_output = Definition(
    name="cargo_audit_output", primitive="Dict[str, Any]"
)


class CargoAuditError(Exception):
    """
    Raised when cargo-audit fails
    """


async def run_cargo_build(pkg_input: str):

    new_proc = await asyncio.create_subprocess_exec(
        "cargo",
        "build",
        "--release",
        cwd=pkg_input,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await new_proc.communicate()
    if new_proc.returncode != 0:
        raise Exception(stderr.decode())


@op(inputs={"pkg": package_src_dir}, outputs={"report": cargo_audit_output})
async def run_cargo_audit(pkg: str) -> Dict[str, Any]:
    """
    CLI usage: dffml service dev run -log debug shouldi.cargo_audit:run_cargo_audit -pkg .
    """
    proc = await asyncio.create_subprocess_exec(
        "cargo",
        "audit",
        "--json",
        cwd=pkg,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if len(stdout) == 0:
        raise CargoAuditError(stderr.decode())

    cargo_audit_op = stdout.decode()
    issues = json.loads(cargo_audit_op)
    result = issues["vulnerabilities"]["count"]

    return {"report": result}
