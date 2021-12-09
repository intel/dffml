from typing import List

from ..df.base import op
from ..df.types import Definition
from ..util.subprocess import Subprocess, exec_subprocess


SUBPROCESS_CMD = Definition(name="subprocess.cmd", primitive="List[str]")
SUBPROCESS_CWD = Definition(
    name="subprocess.cwd", primitive="str", default=None,
)
SUBPROCESS_STDOUT = Definition(name="subprocess.stdout", primitive="str")
SUBPROCESS_STDERR = Definition(name="subprocess.stderr", primitive="str")
SUBPROCESS_RETURN_CODE = Definition(
    name="subprocess.returncode", primitive="int"
)


@op(
    inputs={"cmd": SUBPROCESS_CMD, "cwd": SUBPROCESS_CWD},
    outputs={
        "stdout": SUBPROCESS_STDOUT,
        "stderr": SUBPROCESS_STDERR,
        "returncode": SUBPROCESS_RETURN_CODE,
    },
)
async def subprocess_line_by_line(self, cmd: List[str], cwd: str = None):
    output = {"stdout": "", "stderr": "", "returncode": 1}
    async for event, result in exec_subprocess(cmd, cwd=cwd):
        if event == Subprocess.STDOUT_READLINE:
            output["stdout"] += result.decode()
            result = result.decode().rstrip()
            self.logger.debug(result)
        elif event == Subprocess.STDERR_READLINE:
            output["stderr"] += result.decode()
            result = result.decode().rstrip()
            self.logger.debug(result)
        elif event == Subprocess.COMPLETED:
            output["returncode"] = result
    return output
