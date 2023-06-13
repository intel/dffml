import pathlib
import textwrap
import itertools
from typing import NamedTuple, NewType, Optional, Type


import dffml
import dffml_feature_git.feature.definitions

from .recommended_community_standards import *


# NOTE Not sure if the orchestrator will know what to do if we do this
# SecurityGitRepo = AliceGitRepo
class SecurityGitRepo(NamedTuple):
    directory: str
    URL: str


@dffml.entrypoint(
    "dffml.overlays.alice.please.contribute.recommended_community_standards.security"
)
class OverlaySECURITY:
    SecurityPath = NewType("SecurityPath", object)
    SecurityContents = NewType("repo.directory.security.contents", str)
    SecurityCommitMessage = NewType("repo.security.git.commit.message", str)
    SecurityBranch = NewType("repo.security.git.branch", str)
    SecurityPR = NewType("SecurityPR", str)
    SecurityIssue = NewType("SecurityIssue", str)
    SecurityIssueBody = NewType("SecurityIssueBody", str)
    SecurityIssueTitle = NewType("SecurityIssueTitle", str)
    SecurityPRTitle = NewType("security.github.pr.title", str)
    SecurityPRBody = NewType("security.github.pr.body", str)

    # async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
    async def alice_contribute_security(self, repo: AliceGitRepo) -> SecurityGitRepo:
        async for ctx, results in dffml.subflow_typecast(
            self, OverlaySECURITY, AliceGitRepoInputSetContext(repo), repo,
        ):
            pass

    # TODO Run this system context where security contexts is given on CLI or
    # overriden via disabling of static overlay and application of overlay to
    # generate contents dynamiclly.
    # aka, test with `-inputs` option
    def create_security_file_if_not_exists(
        self,
        repo: SecurityGitRepo,
        security_contents: Optional["SecurityContents"] = "# My Awesome Project's SECURITY",
    ) -> "SecurityPath":
        # Do not create security if it already exists
        path = pathlib.Path(repo.directory, "SECURITY.md")
        if path.exists():
            return path
        path.write_text(security_contents)
        return path

    async def contribute_security_md(
        self,
        repo: SecurityGitRepo,
        base: OverlayGit.BaseBranch,
        commit_message: "SecurityCommitMessage",
    ) -> "SecurityBranch":
        branch_name: str = "alice-contribute-recommended-community-standards-security"
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
            ["git", "add", "SECURITY.md"], cwd=repo.directory, logger=self.logger,
        )
        await dffml.run_command(
            ["git", "commit", "-sm", commit_message],
            cwd=repo.directory,
            logger=self.logger,
        )
        return branch_name

    async def security_pr(
        self,
        repo: SecurityGitRepo,
        base: OverlayGit.BaseBranch,
        origin: OverlayGit.WriteableGitRemoteOrigin,
        head: "SecurityBranch",
        title: "SecurityPRTitle",
        body: "SecurityPRBody",
    ) -> "SecurityPR":
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
    async def security_issue(
        self,
        repo: SecurityGitRepo,
        title: Optional["SecurityIssueTitle"] = "Recommended Community Standard: SECURITY",
        body: Optional[
            "SecurityIssueBody"
        ] = "References:\n- https://docs.github.com/articles/about-securitys/",
    ) -> "SecurityIssue":
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
    def security_commit_message(issue_url: "SecurityIssue",) -> "SecurityCommitMessage":
        return textwrap.dedent(
            f"""
            Recommended Community Standard: SECURITY

            Closes: {issue_url}
            """
        ).lstrip()

    @staticmethod
    async def security_pr_body(security_issue: "SecurityIssue",) -> "SecurityPRBody":
        return f"Closes: {security_issue}"

    async def security_pr_title(self, security_issue: "SecurityIssue",) -> "SecurityPRTitle":
        """
        Use the issue title as the pull request title
        """
        async for event, result in dffml.run_command_events(
            ["gh", "issue", "view", "--json", "title", "-q", ".title", security_issue,],
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                return result.strip().decode()
