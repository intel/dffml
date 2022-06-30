import os
import sys
import copy
import pathlib
import inspect
import textwrap
import unittest
import platform
import itertools
import contextlib
import dataclasses
from typing import Dict, List, Optional, AsyncIterator, NamedTuple, NewType


import dffml

from ....recommended_community_standards import AliceGitRepo, AlicePleaseContributeRecommendedCommunityStandards
from ....dffml.operations.git.contribute import AlicePleaseContributeRecommendedCommunityStandardsOverlayGit
from .issue import AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue


# TODO Spawn background task (could use an orchestrator which creates a
# GitHub Actions cron job to execute later). set_close_meta_issue_trigger
class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest:
    ReadmePR = NewType("ReadmePR", str)
    Title = NewType("github.pr.title", str)
    Body = NewType("github.pr.body", str)
    WriteableGitRemoteOrigin = NewType("writable.github.remote.origin", str)

    async def readme_pr(
        self,
        repo: AliceGitRepo,
        base: AlicePleaseContributeRecommendedCommunityStandardsOverlayGit.BaseBranch,
        origin: "WriteableGitRemoteOrigin",
        head: AlicePleaseContributeRecommendedCommunityStandardsOverlayGit.ReadmeBranch,
        title: "Title",
        body: "Body",
    ) -> "ReadmePR":
        """

        Check if we have any other issues open for the repo

        .. code-block:: console
            :exec:

            $ gh issue -R "${GITHUB_REPO_URL}" create --title "Recommended Community Standards (alice)" --body "${META_ISSUE_BODY}"

        """
        # Ensure an origin we can write to has an up to date version of head
        # with what we have locally so that GitHub can reference that branch for
        # the pull request.
        await dffml.run_command(
            # TODO Remove -f
            ["git", "push", "-fu", origin, head], cwd=repo.directory, logger=self.logger,
        )
        await dffml.run_command(
            [
                "gh",
                "pr",
                "create",
                "--base",
                base,
                "--head",
                head,
                "--title",
                title,
                "--body",
                body,
            ],
            cwd=repo.directory,
            logger=self.logger,
        )


class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequestReferenceIssue:
    @staticmethod
    async def readme_pr_body(
        readme_issue: AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue.ReadmeIssue,
    ) -> AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest.Body:
        return f"Closes: {readme_issue}"

    async def readme_pr_title(
        self,
        readme_issue: AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue.ReadmeIssue,
    ) -> AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest.Title:
        """
        Use the issue title as the pull request title
        """
        async for event, result in dffml.run_command_events(
            ["gh", "issue", "view", "--json", "title", "-q", ".title", readme_issue,],
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                return result.strip().decode()
