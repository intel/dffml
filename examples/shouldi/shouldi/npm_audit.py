import json
import asyncio
from typing import Dict, Any

from dffml.df.base import op
from dffml.df.types import Definition

package_src_dir = Definition(name="package_src_dir", primitive="str")
npm_audit_output = Definition(
    name="npm_audit_output", primitive="Dict[str, Any]"
)


class NPM_AuditError(Exception):
    """
    Raised when npm-audit fails
    """


@op(inputs={"pkg": package_src_dir}, outputs={"report": npm_audit_output})
async def run_npm_audit(pkg: str) -> Dict[str, Any]:
    """
    CLI usage: dffml service dev run -log debug shouldi.npm_audit:run_npm_audit -pkg .
    """
    proc = await asyncio.create_subprocess_exec(
        "npm",
        "audit",
        "--json",
        cwd=pkg,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, _stderr = await proc.communicate()
    if len(stdout) == 0:
        raise NPM_AuditError(_stderr)

    npm_audit_op = stdout.decode()
    npm_audit_op = json.loads(npm_audit_op)
    result = npm_audit_op["metadata"]["vulnerabilities"]
    return result
