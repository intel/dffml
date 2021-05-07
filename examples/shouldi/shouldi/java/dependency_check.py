import json
import os
import tempfile
import urllib.parse
from pathlib import Path
import asyncio
from typing import Dict, Any

from dffml import op, Definition, concurrently

package_src_dir = Definition(name="package_src_dir", primitive="str")
dependency_check_output = Definition(
    name="dependency_check_output", primitive="Dict[str, Any]"
)


class DependencyCheckError(Exception):
    """
    Raised when dependency-check fails
    """


@op(
    inputs={"pkg": package_src_dir},
    outputs={"report": dependency_check_output},
)
async def run_dependency_check(self, pkg: str) -> Dict[str, Any]:
    """
    CLI usage: dffml service dev run -log debug shouldi.dependency_check:run_dependency_check -pkg .
    """
    with tempfile.TemporaryDirectory() as tempdir:
        # Define command
        cmd = [
            "dependency-check.sh",
            "-f",
            "JSON",
            "--out",
            os.path.abspath(tempdir),
        ]
        kwargs = {
            "stdout": asyncio.subprocess.PIPE,
            "stderr": asyncio.subprocess.PIPE,
        }
        # Dependency check version 6 requires proxy be set explicitly
        for env_var in ["HTTPS_PROXY", "https_proxy"]:
            if env_var in os.environ:
                parse_result = urllib.parse.urlparse(os.environ[env_var])
                cmd += [
                    "--proxyserver",
                    parse_result.hostname,
                    "--proxyport",
                    str(parse_result.port)
                    if parse_result.port is not None
                    else "8080",
                ]
                break
        # Directory or file to scan
        cmd.append("-s")
        if Path(pkg).is_file():
            cmd.append(os.path.basename(pkg))
            kwargs["cwd"] = os.path.dirname(pkg)
        else:
            cmd.append(".")
            kwargs["cwd"] = pkg
        # Run command
        self.logger.debug(f"Running {cmd}, {kwargs}")
        proc = await asyncio.create_subprocess_exec(*cmd, **kwargs)
        output = []
        work = {
            asyncio.create_task(proc.stdout.readline()): "stdout.readline",
            asyncio.create_task(proc.stderr.readline()): "stderr.readline",
            asyncio.create_task(proc.wait()): "wait",
        }
        async for event, result in concurrently(work):
            if event.endswith("readline"):
                # Log line read
                self.logger.debug(f"{event}: {result.decode().rstrip()}")
                # Append to output in case of error
                output.append(result)
                # Read another line if that's the event
                coro = getattr(proc, event.split(".")[0]).readline()
                task = asyncio.create_task(coro)
                work[task] = event
            else:
                # When wait() returns process has exited
                break

        if proc.returncode != 0:
            raise DependencyCheckError(b"\n".join(output).decode())

        with open(
            os.path.join(
                os.path.abspath(tempdir), "dependency-check-report.json"
            )
        ) as f:
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
