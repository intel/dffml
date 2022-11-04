import logging
from typing import Optional

import dffml


async def gh_issue_create(
    repo_url: str,
    title: str,
    body: str,
    logger: Optional[logging.Logger] = None,
) -> str:
    async for event, result in dffml.run_command_events(
        [
            "gh",
            "issue",
            "create",
            "-R",
            repo_url,
            "--title",
            title,
            "--body",
            body,
        ],
        logger=logger,
        events=[dffml.Subprocess.STDOUT],
    ):
        if event is dffml.Subprocess.STDOUT:
            # The URL of the issue created
            return result.strip().decode()
