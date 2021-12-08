from typing import List

from ..df.base import op
from ..util.subprocess import exec_subprocess


@op
async def subprocess_line_by_line(self, cmd: List[str], cwd: str = None):
    output = {"stdout": "", "stderr": "", "returncode": 1}
    async for event, result in exec_subprocess(cmd, cwd=cwd):
        if event == Subprocess.STDOUT_READLINE:
            output["stdout"] += result.decode()
            result = result.decode().rstrip()
            self.logger.debug(f"{cmd}: {event}: {result}")
        elif event == Subprocess.STDERR_READLINE:
            output["stderr"] += result.decode()
            result = result.decode().rstrip()
            self.logger.error(f"{cmd}: {event}: {result}")
        elif event == Subprocess.COMPLETED:
            output["returncode"] = result
    return output
