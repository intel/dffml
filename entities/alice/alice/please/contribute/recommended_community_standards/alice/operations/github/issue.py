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



class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:
    """

    Check if we have any other issues open for the repo

    .. code-block:: console
        :test:

        $ gh issue -R "${GITHUB_REPO}" list --search "Recommended Community Standard"
        no issues match your search in intel/dffml

    """

    ReadmeIssue = NewType("ReadmeIssue", str)
    ReadmeIssueTitle = NewType("ReadmeIssueTitle", str)
    ReadmeIssueBody = NewType("ReadmeIssueBody", str)
    MetaIssue = NewType("MetaIssue", str)
    MetaIssueTitle = NewType("MetaIssueTitle", str)
    MetaIssueBody = NewType("MetaIssueBody", str)

    # body: Optional['ContributingIssueBody'] = "References:\n- https://docs.github.com/articles/setting-guidelines-for-repository-contributors/",
    async def readme_issue(
        self,
        repo: AliceGitRepo,
        title: Optional["ReadmeIssueTitle"] = "Recommended Community Standard: README",
        body: Optional[
            "ReadmeIssueBody"
        ] = "References:\n- https://docs.github.com/articles/about-readmes/",
    ) -> "ReadmeIssue":
        async for event, result in dffml.run_command_events(
            [
                "gh",
                "issue",
                "create",
                "-R",
                repo.URL,
                "--title",
                title,
                "--body",
                body,
            ],
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                # The URL of the issue created
                return result.strip().decode()

    @staticmethod
    def readme_commit_message(
        issue_url: "ReadmeIssue",
    ) -> AlicePleaseContributeRecommendedCommunityStandardsOverlayGit.ReadmeCommitMessage:
        return textwrap.dedent(
            f"""
            Recommended Community Standard: README

            Closes: {issue_url}
            """
        ).lstrip()

    # TODO(alice) There is a bug with Optional which can be revield by use here
    @staticmethod
    def meta_issue_body(
        repo: AliceGitRepo,
        base: AlicePleaseContributeRecommendedCommunityStandardsOverlayGit.BaseBranch,
        readme_path: AlicePleaseContributeRecommendedCommunityStandards.ReadmePath,
        readme_issue: ReadmeIssue,
    ) -> "MetaIssueBody":
        """
        >>> AlicePleaseContributeRecommendedCommunityStandardsGitHubIssueOverlay.meta_issue_body(
        ...     repo=AliceGitRepo(
        ...     ),
        ... )
        - [] [README](https://github.com/intel/dffml/blob/main/README.md)
        - [] Code of conduct
        - [] [Contributing](https://github.com/intel/dffml/blob/main/CONTRIBUTING.md)
        - [] [License](https://github.com/intel/dffml/blob/main/LICENSE)
        - [] Security
        """
        return "\n".join(
            [
                "- ["
                + ("x" if readme_issue is None else " ")
                + "] "
                + (
                    "README: " + readme_issue
                    if readme_issue is not None
                    else f"[README]({repo.URL}/blob/{base}/{readme_path.relative_to(repo.directory).as_posix()})"
                ),
            ]
        )

    async def create_meta_issue(
        self,
        repo: AliceGitRepo,
        body: "MetaIssueBody",
        title: Optional["MetaIssueTitle"] = "Recommended Community Standards",
    ) -> "MetaIssue":
        async for event, result in dffml.run_command_events(
            [
                "gh",
                "issue",
                "create",
                "-R",
                repo.URL,
                "--title",
                title,
                "--body",
                body,
            ],
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                # The URL of the issue created
                return result.strip().decode()
