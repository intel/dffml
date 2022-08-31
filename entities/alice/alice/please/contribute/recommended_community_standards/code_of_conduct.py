import pathlib
import textwrap
import itertools
from typing import NamedTuple, NewType, Optional, Type


import dffml
import dffml_feature_git.feature.definitions

from .recommended_community_standards import *


# NOTE Not sure if the orchestrator will know what to do if we do this
# CodeOfConductGitRepo = AliceGitRepo
class CodeOfConductGitRepo(NamedTuple):
    directory: str
    URL: str


@dffml.entrypoint(
    "dffml.overlays.alice.please.contribute.recommended_community_standards.code_of_conduct"
)
class OverlayCODE_OF_CONDUCT:
    CodeOfConductPath = NewType("CodeOfConductPath", object)
    CodeOfConductContents = NewType("repo.directory.code_of_conduct.contents", str)
    CodeOfConductCommitMessage = NewType("repo.code_of_conduct.git.commit.message", str)
    CodeOfConductBranch = NewType("repo.code_of_conduct.git.branch", str)
    CodeOfConductPR = NewType("CodeOfConductPR", str)
    CodeOfConductIssue = NewType("CodeOfConductIssue", str)
    CodeOfConductIssueBody = NewType("CodeOfConductIssueBody", str)
    CodeOfConductIssueTitle = NewType("CodeOfConductIssueTitle", str)
    CodeOfConductPRTitle = NewType("code_of_conduct.github.pr.title", str)
    CodeOfConductPRBody = NewType("code_of_conduct.github.pr.body", str)

    # async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
    async def alice_contribute_code_of_conduct(self, repo: AliceGitRepo) -> CodeOfConductGitRepo:
        async for ctx, results in dffml.subflow_typecast(
            self, OverlayCODE_OF_CONDUCT, AliceGitRepoInputSetContext(repo), repo,
        ):
            pass

    # TODO Run this system context where code_of_conduct contexts is given on CLI or
    # overriden via disabling of static overlay and application of overlay to
    # generate contents dynamiclly.
    # aka, test with `-inputs` option
    def create_code_of_conduct_file_if_not_exists(
        self,
        repo: CodeOfConductGitRepo,
        code_of_conduct_contents: Optional["CodeOfConductContents"] = "# My Awesome Project's CODE_OF_CONDUCT",
    ) -> "CodeOfConductPath":
        # Do not create code_of_conduct if it already exists
        path = pathlib.Path(repo.directory, "CODE_OF_CONDUCT.md")
        if path.exists():
            return path
        path.write_text(code_of_conduct_contents)
        return path

    async def contribute_code_of_conduct_md(
        self,
        repo: CodeOfConductGitRepo,
        base: OverlayGit.BaseBranch,
        commit_message: "CodeOfConductCommitMessage",
    ) -> "CodeOfConductBranch":
        branch_name: str = "alice-contribute-recommended-community-standards-code_of_conduct"
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
            ["git", "add", "CODE_OF_CONDUCT.md"], cwd=repo.directory, logger=self.logger,
        )
        await dffml.run_command(
            ["git", "commit", "-sm", commit_message],
            cwd=repo.directory,
            logger=self.logger,
        )
        return branch_name

    async def code_of_conduct_pr(
        self,
        repo: CodeOfConductGitRepo,
        base: OverlayGit.BaseBranch,
        origin: OverlayGit.WriteableGitRemoteOrigin,
        head: "CodeOfConductBranch",
        title: "CodeOfConductPRTitle",
        body: "CodeOfConductPRBody",
    ) -> "CodeOfConductPR":
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
    async def code_of_conduct_issue(
        self,
        repo: CodeOfConductGitRepo,
        title: Optional["CodeOfConductIssueTitle"] = "Recommended Community Standard: CODE_OF_CONDUCT",
        body: Optional[
            "CodeOfConductIssueBody"
        ] = "References:\n- https://docs.github.com/articles/about-code_of_conducts/",
    ) -> "CodeOfConductIssue":
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
    def code_of_conduct_commit_message(issue_url: "CodeOfConductIssue",) -> "CodeOfConductCommitMessage":
        return textwrap.dedent(
            f"""
            Recommended Community Standard: CODE_OF_CONDUCT

            Closes: {issue_url}
            """
        ).lstrip()

    @staticmethod
    async def code_of_conduct_pr_body(code_of_conduct_issue: "CodeOfConductIssue",) -> "CodeOfConductPRBody":
        return f"Closes: {code_of_conduct_issue}"

    async def code_of_conduct_pr_title(self, code_of_conduct_issue: "CodeOfConductIssue",) -> "CodeOfConductPRTitle":
        """
        Use the issue title as the pull request title
        """
        async for event, result in dffml.run_command_events(
            ["gh", "issue", "view", "--json", "title", "-q", ".title", code_of_conduct_issue,],
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                return result.strip().decode()
