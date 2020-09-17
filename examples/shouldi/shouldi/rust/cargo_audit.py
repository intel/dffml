import os
import json
import asyncio
import itertools
import contextlib
from typing import Dict, Any

from dffml import op, Definition, traverse_get

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

    cargo_report = json.loads(stdout.decode())

    spec = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for vuln in itertools.chain(
        cargo_report["vulnerabilities"]["list"], cargo_report["warnings"],
    ):
        cvss = None
        for path in [
            ("kind", "unmaintained", "advisory", "cvss"),
            ("advisory", "cvss"),
        ]:
            # Handle kind is "yanked" case
            with contextlib.suppress(KeyError, TypeError):
                cvss = traverse_get(vuln, *path)
                if cvss is None or isinstance(cvss, (float, int)):
                    break
        if cvss is None:
            cvss = 0

        # Rating   | CVSS Score
        # ---------+-------------
        # None     | 0.0
        # Low      | 0.1 - 3.9
        # Medium   | 4.0 - 6.9
        # High     | 7.0 - 8.9
        # Critical | 9.0 - 10.0
        #
        # Source: https://www.first.org/cvss/specification-document
        if cvss >= 9.0:
            spec["critical"] += 1
        elif cvss >= 7.0:
            spec["high"] += 1
        elif cvss >= 4.0:
            spec["medium"] += 1
        else:
            spec["low"] += 1

    cargo_report["qualitative"] = spec

    return {"report": cargo_report}
