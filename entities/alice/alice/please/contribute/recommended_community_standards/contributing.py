import pathlib
import textwrap
import itertools
from typing import NamedTuple, NewType, Optional, Type


import dffml
import dffml_feature_git.feature.definitions

from .recommended_community_standards import *


# NOTE Not sure if the orchestrator will know what to do if we do this
# ContributingGitRepo = AliceGitRepo
class ContributingGitRepo(NamedTuple):
    directory: str
    URL: str


@dffml.entrypoint(
    "dffml.overlays.alice.please.contribute.recommended_community_standards.contributing"
)
class OverlayCONTRIBUTING:
    ContributingPath = NewType("ContributingPath", object)
    ContributingContents = NewType("repo.directory.contributing.contents", str)
    ContributingCommitMessage = NewType("repo.contributing.git.commit.message", str)
    ContributingBranch = NewType("repo.contributing.git.branch", str)
    ContributingPR = NewType("ContributingPR", str)
    ContributingIssue = NewType("ContributingIssue", str)
    ContributingIssueBody = NewType("ContributingIssueBody", str)
    ContributingIssueTitle = NewType("ContributingIssueTitle", str)
    ContributingPRTitle = NewType("contributing.github.pr.title", str)
    ContributingPRBody = NewType("contributing.github.pr.body", str)

    # async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
    async def alice_contribute_contributing(
        self, repo: AliceGitRepo
    ) -> ContributingGitRepo:
        async for ctx, results in dffml.subflow_typecast(
            self, OverlayCONTRIBUTING, AliceGitRepoInputSetContext(repo), repo,
        ):
            pass

    # TODO Run this system context where contributing contexts is given on CLI or
    # overriden via disabling of static overlay and application of overlay to
    # generate contents dynamiclly.
    # aka, test with `-inputs` option
    def create_contributing_file_if_not_exists(
        self,
        repo: ContributingGitRepo,
        contributing_contents: Optional[
            "ContributingContents"
        ] = "# My Awesome Project's CONTRIBUTING",
    ) -> "ContributingPath":
        # Do not create contributing if it already exists
        path = pathlib.Path(repo.directory, "CONTRIBUTING.md")
        if path.exists():
            return path
        path.write_text(contributing_contents)
        return path

    async def contribute_contributing_md(
        self,
        repo: ContributingGitRepo,
        base: OverlayGit.BaseBranch,
        commit_message: "ContributingCommitMessage",
    ) -> "ContributingBranch":
        branch_name: str = "alice-contribute-recommended-community-standards-contributing"
        # Attempt multiple commands
        async for event, result in dffml.run_command_events(
            ["git", "checkout", base, "-b", branch_name,],
            cwd=repo.directory,
            logger=self.logger,
            raise_on_failure=False,
            events=[dffml.Subprocess.STDERR, dffml.Subprocess.COMPLETED,],
        ):
            if event is dffml.Subprocess.STDERR:
                if b"is not a commit and a branch" in result:
                    # Retry without explict branch when repo has no commits
                    await dffml.run_command(
                        ["git", "checkout", "-b", branch_name,],
                        cwd=repo.directory,
                        logger=self.logger,
                    )
            elif event is dffml.Subprocess.COMPLETED:
                if result != 0:
                    raise RuntimeError("Failed to create branch for contribution")
        await dffml.run_command(
            ["git", "add", "CONTRIBUTING.md"], cwd=repo.directory, logger=self.logger,
        )
        await dffml.run_command(
            ["git", "commit", "-sm", commit_message],
            cwd=repo.directory,
            logger=self.logger,
        )
        return branch_name

    async def contributing_pr(
        self,
        repo: ContributingGitRepo,
        base: OverlayGit.BaseBranch,
        origin: OverlayGit.WriteableGitRemoteOrigin,
        head: "ContributingBranch",
        title: "ContributingPRTitle",
        body: "ContributingPRBody",
    ) -> "ContributingPR":
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
            ["git", "push", "-fu", origin, head],
            cwd=repo.directory,
            logger=self.logger,
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

    # body: Optional['ContributingIssueBody'] = "References:\n- https://docs.github.com/articles/setting-guidelines-for-repository-contributors/",
    async def contributing_issue(
        self,
        repo: ContributingGitRepo,
        title: Optional[
            "ContributingIssueTitle"
        ] = "Recommended Community Standard: CONTRIBUTING",
        body: Optional[
            "ContributingIssueBody"
        ] = "References:\n- https://docs.github.com/articles/about-contributings/",
    ) -> "ContributingIssue":
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
    def contributing_commit_message(
        issue_url: "ContributingIssue",
    ) -> "ContributingCommitMessage":
        return textwrap.dedent(
            f"""
            Recommended Community Standard: CONTRIBUTING

            Closes: {issue_url}
            """
        ).lstrip()

    @staticmethod
    async def contributing_pr_body(
        contributing_issue: "ContributingIssue",
    ) -> "ContributingPRBody":
        return f"Closes: {contributing_issue}"

    async def contributing_pr_title(
        self, contributing_issue: "ContributingIssue",
    ) -> "ContributingPRTitle":
        """
        Use the issue title as the pull request title
        """
        async for event, result in dffml.run_command_events(
            [
                "gh",
                "issue",
                "view",
                "--json",
                "title",
                "-q",
                ".title",
                contributing_issue,
            ],
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                return result.strip().decode()
