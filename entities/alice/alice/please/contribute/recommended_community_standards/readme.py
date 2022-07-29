import pathlib
import textwrap
import itertools
from typing import NamedTuple, NewType, Optional, Type


import dffml
import dffml_feature_git.feature.definitions

from .recommended_community_standards import *


# NOTE Not sure if the orchestrator will know what to do if we do this
# ReadmeGitRepo = AliceGitRepo
class ReadmeGitRepo(NamedTuple):
    directory: str
    URL: str


@dffml.entrypoint(
    "dffml.overlays.alice.please.contribute.recommended_community_standards.readme"
)
class OverlayREADME:
    ReadmePath = NewType("ReadmePath", object)
    ReadmeContents = NewType("repo.directory.readme.contents", str)
    ReadmeCommitMessage = NewType("repo.readme.git.commit.message", str)
    ReadmeBranch = NewType("repo.readme.git.branch", str)
    ReadmePR = NewType("ReadmePR", str)
    ReadmeIssue = NewType("ReadmeIssue", str)
    ReadmeIssueBody = NewType("ReadmeIssueBody", str)
    ReadmeIssueTitle = NewType("ReadmeIssueTitle", str)
    ReadmePRTitle = NewType("readme.github.pr.title", str)
    ReadmePRBody = NewType("readme.github.pr.body", str)

    # async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
    async def alice_contribute_readme(self, repo: AliceGitRepo) -> ReadmeGitRepo:
        async for ctx, results in dffml.subflow_typecast(
            self, OverlayREADME, AliceGitRepoInputSetContext(repo), repo,
        ):
            pass

    # TODO Run this system context where readme contexts is given on CLI or
    # overriden via disabling of static overlay and application of overlay to
    # generate contents dynamiclly.
    # aka, test with `-inputs` option
    def create_readme_file_if_not_exists(
        self,
        repo: ReadmeGitRepo,
        readme_contents: Optional["ReadmeContents"] = "# My Awesome Project's README",
    ) -> "ReadmePath":
        # Do not create readme if it already exists
        path = pathlib.Path(repo.directory, "README.md")
        if path.exists():
            return path
        path.write_text(readme_contents)
        return path

    async def contribute_readme_md(
        self,
        repo: ReadmeGitRepo,
        base: OverlayGit.BaseBranch,
        commit_message: "ReadmeCommitMessage",
    ) -> "ReadmeBranch":
        branch_name: str = "alice-contribute-recommended-community-standards-readme"
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
            ["git", "add", "README.md"], cwd=repo.directory, logger=self.logger,
        )
        await dffml.run_command(
            ["git", "commit", "-sm", commit_message],
            cwd=repo.directory,
            logger=self.logger,
        )
        return branch_name

    async def readme_pr(
        self,
        repo: ReadmeGitRepo,
        base: OverlayGit.BaseBranch,
        origin: OverlayGit.WriteableGitRemoteOrigin,
        head: "ReadmeBranch",
        title: "ReadmePRTitle",
        body: "ReadmePRBody",
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
    async def readme_issue(
        self,
        repo: ReadmeGitRepo,
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
    def readme_commit_message(issue_url: "ReadmeIssue",) -> "ReadmeCommitMessage":
        return textwrap.dedent(
            f"""
            Recommended Community Standard: README

            Closes: {issue_url}
            """
        ).lstrip()

    @staticmethod
    async def readme_pr_body(readme_issue: "ReadmeIssue",) -> "ReadmePRBody":
        return f"Closes: {readme_issue}"

    async def readme_pr_title(self, readme_issue: "ReadmeIssue",) -> "ReadmePRTitle":
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
