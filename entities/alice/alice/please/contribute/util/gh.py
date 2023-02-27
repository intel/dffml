import json
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


async def gh_issue_update(
    issue_url: str,
    title: str,
    body: str,
    *,
    logger: Optional[logging.Logger] = None,
) -> str:
    async for event, result in dffml.run_command_events(
        [
            "gh",
            "issue",
            "edit",
            issue_url,
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


async def gh_issue_search_by_title(
    repo_url: str,
    title: str,
    *,
    logger: Optional[logging.Logger] = None,
) -> str:
    # TODO Add kwarg filter for author
    async for event, result in dffml.run_command_events(
        [
            "gh",
            "issue",
            "list",
            "-R",
            repo_url,
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
    # Try to find an exsiting issue with the same title
    found_issue_to_update = None
    async for issue in gh_issue_search_by_title(
        repo_url,
        title,
        logger=logger,
    ):
        # TODO Data model from data model generation from schema
        if issue["title"] == title and issue["state"] == "OPEN":
            found_issue_to_update = issue
    # If we don't find it, create it
    if not found_issue_to_update:
        return await gh_issue_create(
            repo_url,
            title,
            body,
            logger=logger,
        )
    # Otherwise update the body of the existing issue
    return await gh_issue_update(
        issue["url"],
        title,
        body,
        logger=logger,
    )
