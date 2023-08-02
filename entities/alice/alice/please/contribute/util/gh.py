import json
import pathlib
import logging
import tempfile
import dataclasses
from typing import Optional

import dffml


@dataclasses.dataclass
class GHAuthStatus:
    username: str


class GHAuthStatusUncapturedError(Exception):
    pass


async def gh_auth_status(
    *,
    logger: Optional[logging.Logger] = None,
) -> str:
    auth_status = GHAuthStatus(
        username=None
    )
    async for event, result in dffml.run_command_events(
        [
            "gh",
            "auth",
            "status",
        ],
        logger=logger,
        events=[dffml.Subprocess.STDOUT_READLINE, dffml.Subprocess.STDERR_READLINE],
    ):
        if event not in (
            dffml.Subprocess.STDOUT_READLINE,
            dffml.Subprocess.STDERR_READLINE,
        ):
            continue
        line = result.strip().decode()
        if "Logged in to" in line:
            auth_status.username = line.split()[-2]
    if not any(auth_status.__dict__.values()):
        raise GHAuthStatusUncapturedError(f"Not all fields were captured: {auth_status!r}")
    if logger:
        logger.debug("%r", auth_status)
    return auth_status


async def gh_issue_create(
    repo_url: str,
    title: str,
    body: str,
    logger: Optional[logging.Logger] = None,
) -> str:
    # Create tempdir to avoid issue body to long
    with tempfile.TemporaryDirectory() as tempdir:
        body_path = pathlib.Path(tempdir, "issue_body.txt")
        body_path.write_text(body)
        async for event, result in dffml.run_command_events(
            [
                "gh",
                "issue",
                "create",
                "-R",
                repo_url,
                "--title",
                title,
                "--body-file",
                str(body_path),
            ],
            logger=logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                # The URL of the issue created
                return result.strip().decode()


async def gh_issue_update(
    issue_url: str,
    title: str,
    body: str,
    *,
    logger: Optional[logging.Logger] = None,
) -> str:
    # Create tempdir to avoid issue body to long
    with tempfile.TemporaryDirectory() as tempdir:
        body_path = pathlib.Path(tempdir, "issue_body.txt")
        body_path.write_text(body)
        async for event, result in dffml.run_command_events(
            [
                "gh",
                "issue",
                "edit",
                issue_url,
                "--title",
                title,
                "--body-file",
                str(body_path),
            ],
            logger=logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                # The URL of the issue created
                return result.strip().decode()


async def gh_issue_close(
    issue_url: str,
    *,
    comment_body: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> str:
    async for event, result in dffml.run_command_events(
        [
            "gh",
            "issue",
            "close",
            issue_url,
        ] + (
            [
                "--comment",
                str(comment_body),
            ] if comment_body is not None else []
        ),
        logger=logger,
        events=[dffml.Subprocess.STDOUT],
    ):
        if event is dffml.Subprocess.STDOUT:
            # The URL of the issue created
            return result.strip().decode()


async def gh_issue_search_by_title(
    repo_url: str,
    title: str,
    *,
    logger: Optional[logging.Logger] = None,
) -> str:
    async for event, result in dffml.run_command_events(
        [
            "gh",
            "issue",
            "list",
            "-R",
            repo_url,
            "--state",
            "all",
            "--search",
            title,
            "--json",
            "title,url,state,author,state",
        ],
        logger=logger,
        events=[dffml.Subprocess.STDOUT],
    ):
        if event is dffml.Subprocess.STDOUT:
            # The URL of the issue created
            for item in json.loads(result.strip().decode()):
                yield item


async def gh_issue_create_or_update_by_title(
    repo_url: str,
    title: str,
    body: str,
    *,
    logger: Optional[logging.Logger] = None,
) -> str:
    # Get user we are logged in as so we only update issues which we have
    # permissions to update.
    auth_status = await gh_auth_status(logger=logger)
    # Try to find an exsiting issue with the same title
    found_issue_to_update = None
    found_issue_to_update_closed = None
    async for issue in gh_issue_search_by_title(
        repo_url,
        title,
        logger=logger,
    ):
        if issue["author"]["login"] != auth_status.username:
            continue
        # TODO Data model from data model generation from schema
        if issue["title"] == title:
            if issue["state"] == "OPEN":
                found_issue_to_update = issue
            else:
                found_issue_to_update_closed = issue
    # If we don't find it, create it
    if found_issue_to_update is None and found_issue_to_update_closed is None:
        return await gh_issue_create(
            repo_url,
            title,
            body,
            logger=logger,
        )
    issue = (
        found_issue_to_update
        if found_issue_to_update
        else found_issue_to_update_closed
    )
    # Otherwise update the body of the existing issue
    return await gh_issue_update(
        issue["url"],
        title,
        body,
        logger=logger,
    )
