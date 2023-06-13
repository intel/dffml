import pathlib
import textwrap
import itertools
from typing import NamedTuple, NewType, Optional, Type


import dffml
import dffml_feature_git.feature.definitions

from .recommended_community_standards import *


# NOTE Not sure if the orchestrator will know what to do if we do this
# SupportGitRepo = AliceGitRepo
class SupportGitRepo(NamedTuple):
    directory: str
    URL: str


@dffml.entrypoint(
    "dffml.overlays.alice.please.contribute.recommended_community_standards.support"
)
class OverlaySUPPORT:
    SupportPath = NewType("SupportPath", object)
    SupportContents = NewType("repo.directory.support.contents", str)
    SupportCommitMessage = NewType("repo.support.git.commit.message", str)
    SupportBranch = NewType("repo.support.git.branch", str)
    SupportPR = NewType("SupportPR", str)
    SupportIssue = NewType("SupportIssue", str)
    SupportIssueBody = NewType("SupportIssueBody", str)
    SupportIssueTitle = NewType("SupportIssueTitle", str)
    SupportPRTitle = NewType("support.github.pr.title", str)
    SupportPRBody = NewType("support.github.pr.body", str)

    # async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
    async def alice_contribute_support(self, repo: AliceGitRepo) -> SupportGitRepo:
        async for ctx, results in dffml.subflow_typecast(
            self, OverlaySUPPORT, AliceGitRepoInputSetContext(repo), repo,
        ):
            pass

    # TODO Run this system context where support contexts is given on CLI or
    # overriden via disabling of static overlay and application of overlay to
    # generate contents dynamiclly.
    # aka, test with `-inputs` option
    def create_support_file_if_not_exists(
        self,
        repo: SupportGitRepo,
        support_contents: Optional["SupportContents"] = "# My Awesome Project's SUPPORT",
    ) -> "SupportPath":
        # Do not create support if it already exists
        path = pathlib.Path(repo.directory, "SUPPORT.md")
        if path.exists():
            return path
        path.write_text(support_contents)
        return path

    async def contribute_support_md(
        self,
        repo: SupportGitRepo,
        base: OverlayGit.BaseBranch,
        commit_message: "SupportCommitMessage",
    ) -> "SupportBranch":
        branch_name: str = "alice-contribute-recommended-community-standards-support"
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
            ["git", "add", "SUPPORT.md"], cwd=repo.directory, logger=self.logger,
        )
        await dffml.run_command(
            ["git", "commit", "-sm", commit_message],
            cwd=repo.directory,
            logger=self.logger,
        )
        return branch_name

    async def support_pr(
        self,
        repo: SupportGitRepo,
        base: OverlayGit.BaseBranch,
        origin: OverlayGit.WriteableGitRemoteOrigin,
        head: "SupportBranch",
        title: "SupportPRTitle",
        body: "SupportPRBody",
    ) -> "SupportPR":
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
    async def support_issue(
        self,
        repo: SupportGitRepo,
        title: Optional["SupportIssueTitle"] = "Recommended Community Standard: SUPPORT",
        body: Optional[
            "SupportIssueBody"
        ] = "References:\n- https://docs.github.com/articles/about-supports/",
    ) -> "SupportIssue":
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
    def support_commit_message(issue_url: "SupportIssue",) -> "SupportCommitMessage":
        return textwrap.dedent(
            f"""
            Recommended Community Standard: SUPPORT

            Closes: {issue_url}
            """
        ).lstrip()

    @staticmethod
    async def support_pr_body(support_issue: "SupportIssue",) -> "SupportPRBody":
        return f"Closes: {support_issue}"

    async def support_pr_title(self, support_issue: "SupportIssue",) -> "SupportPRTitle":
        """
        Use the issue title as the pull request title
        """
        async for event, result in dffml.run_command_events(
            ["gh", "issue", "view", "--json", "title", "-q", ".title", support_issue,],
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                return result.strip().decode()
