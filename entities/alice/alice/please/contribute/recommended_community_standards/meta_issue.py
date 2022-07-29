import pathlib
import textwrap
import itertools
from typing import NamedTuple, NewType, Optional, Type


import dffml
import dffml_feature_git.feature.definitions

from .recommended_community_standards import *


class OverlayMetaIssue:
    """

    Check if we have any other issues open for the repo

    .. code-block:: console
        :test:

        $ gh issue -R "${GITHUB_REPO}" list --search "Recommended Community Standard"
        no issues match your search in intel/dffml

    """

    MetaIssue = NewType("MetaIssue", str)
    MetaIssueTitle = NewType("MetaIssueTitle", str)
    MetaIssueBody = NewType("MetaIssueBody", str)

    # TODO(alice) There is a bug with Optional which can be revield by use here
    @staticmethod
    def meta_issue_body(
        repo: AliceGitRepo,
        base: OverlayGit.BaseBranch,
        readme_path: OverlayREADME.ReadmePath,
        readme_issue: OverlayREADME.ReadmeIssue,
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
        # TODO Spawn background task (could use an orchestrator which creates a
        # GitHub Actions cron job to execute later).
        # set_close_meta_issue_trigger.
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
