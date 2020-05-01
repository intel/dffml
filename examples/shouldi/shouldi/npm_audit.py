import json
import asyncio
from typing import Dict, Any

from dffml import op
from dffml import Definition

package_src_dir = Definition(name="package_src_dir", primitive="str")
npm_audit_output = Definition(
    name="npm_audit_output", primitive="Dict[str, Any]"
)


class NPMAuditError(Exception):
    """
    Raised when npm-audit fails
    """


@op(inputs={"pkg": package_src_dir}, outputs={"report": npm_audit_output})
async def run_npm_audit(self, pkg: str) -> Dict[str, Any]:
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

    stdout, stderr = await proc.communicate()
    if proc.returncode != 0 and stderr:
        raise NPMAuditError(stderr.decode())

    npm_audit_op = stdout.decode()
    try:
        npm_audit_op = json.loads(npm_audit_op)
    except json.decoder.JSONDecodeError:
        self.logger.error("npm audit --json %r: %s", pkg, npm_audit_op)
        raise

    result = npm_audit_op["metadata"]["vulnerabilities"]

    return {"report": result}
