from typing import List

from ..df.base import op
from ..util.subprocess import run_command


@op
async def pip_install(
    self, packages: List[str], upgrade: bool = False
) -> List[str]:
    await run_command(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            *(["-U"] if upgrade else []),
            *packages,
        ],
        logger=self.logger,
    )
    return packages
