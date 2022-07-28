import pathlib
import textwrap
from typing import NamedTuple, NewType, Optional


import dffml
import dffml_feature_git.feature.definitions


class AliceGitRepo(NamedTuple):
    directory: str
    URL: str


class AlicePleaseContributeRecommendedCommunityStandards:
    ReadmePath = NewType("ReadmePath", object)
    RepoString = NewType("repo.string", str)
    ReadmeContents = NewType("repo.directory.readme.contents", str)
    HasReadme = NewType("repo.directory.readme.exists", bool)

    async def guess_repo_string_is_directory(
        repo_string: "RepoString",
    ) -> AliceGitRepo:
        # TODO(security) How bad is this?
        if not pathlib.Path(repo_string).is_dir():
            return
        return AliceGitRepo(directory=repo_string, URL=None)

    # TODO Run this system context where readme contexts is given on CLI or
    # overriden via disabling of static overlay and application of overlay to
    # generate contents dynamiclly.
    # aka, test with `-inputs` option
    def create_readme_file_if_not_exists(
        self,
        repo: AliceGitRepo,
        readme_contents: Optional["ReadmeContents"] = "# My Awesome Project's README",
    ) -> "ReadmePath":
        # Do not create readme if it already exists
        path = pathlib.Path(repo.directory, "README.md")
        if path.exists():
            return path
        path.write_text(readme_contents)
        return path


class AlicePleaseContributeRecommendedCommunityStandardsOverlayAliceOperationsGit:
    def git_repo_to_alice_git_repo(
        repo: dffml_feature_git.feature.definitions.git_repository,
    ) -> AliceGitRepo:
        return repo


# This overlay has a suggested companion overlay of
# AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit due to
# it providing inputs this overlay needs, could suggest to use overlays together
# based of this info.
class AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:
    ReadmeCommitMessage = NewType("repo.readme.git.commit.message", str)
    ReadmeBranch = NewType("repo.readme.git.branch", str)
    BaseBranch = NewType("repo.git.base.branch", str)

    @staticmethod
    def determin_base_branch(
        default_branch: dffml_feature_git.feature.definitions.GitBranchType,
    ) -> "BaseBranch":
        # TODO .tools/process.yml which defines branches to contibute to under
        # different circumstances. Model with Linux kernel for complex case,
        # take KVM.
        # Later do NLP on contributing docs to determine
        return default_branch

    async def contribute_readme_md(
        self,
        repo: AliceGitRepo,
        base: "BaseBranch",
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


async def github_owns_remote(
    self, directory: str, check_remote: str, *, logger=None,
) -> bool:
    remotes = {}
    async for event, result in dffml.run_command_events(
        ["git", "remote", "-v"],
        cwd=directory,
        logger=logger,
        events=[dffml.Subprocess.STDOUT_READLINE],
    ):
        if event is dffml.Subprocess.STDOUT_READLINE:
            remote, url_and_usages = result.decode().strip().split("\t", maxsplit=2)
            if remote != check_remote:
                continue
            url = url_and_usages.split()[0]
            async for event, result in dffml.run_command_events(
                [
                    "gh",
                    "repo",
                    "view",
                    url,
                    "--json",
                    "viewerPermission",
                    "-q",
                    ".viewerPermission",
                ],
                logger=logger,
                events=[dffml.Subprocess.STDOUT],
            ):
                result = result.strip().decode()
                if event is dffml.Subprocess.STDOUT and result in ("ADMIN", "MAINTAIN"):
                    return True
    return False


class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubWritableRemotesFromPermissions:
    async def github_owns_remote(
        self,
        repo: AliceGitRepo,
        remote: dffml_feature_git.feature.definitions.git_remote,
    ) -> AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest.WriteableGitRemoteOrigin:
        if repo.URL is None or not await github_owns_remote(
            self, repo.directory, remote, logger=self.logger
        ):
            return
        return remote


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


# An overlay which could be installed if you have dffml-feature-git
# (aka dffml-operations-git) installed.
class AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:
    GuessedGitURL = NewType("guessed.git.url", bool)
    DefaultBranchName = NewType("default.branch.name", str)

    # The operations we use defined elsewhere
    check_if_valid_git_repository_URL = (
        dffml_feature_git.feature.operations.check_if_valid_git_repository_URL
    )
    clone_git_repo = dffml_feature_git.feature.operations.clone_git_repo
    git_repo_default_branch = (
        dffml_feature_git.feature.operations.git_repo_default_branch
    )

    def guess_repo_string_is_url(
        self,
        repo_string: AlicePleaseContributeRecommendedCommunityStandards.RepoString,
    ) -> GuessedGitURL:
        if "://" not in repo_string:
            return
        return repo_string

    def guessed_repo_string_means_no_git_branch_given(
        repo_url: GuessedGitURL,
    ) -> dffml_feature_git.feature.definitions.NoGitBranchGivenType:
        # TODO Support _ prefixed unused variables (repo_url used to trigger,
        # always true on trigger).
        return True

    def guessed_repo_string_is_operations_git_url(
        repo_url: GuessedGitURL,
    ) -> dffml_feature_git.feature.definitions.URLType:
        return repo_url

    async def create_branch_if_none_exists(
        self, repo: AliceGitRepo, name: Optional["DefaultBranchName"] = "main",
    ) -> dffml_feature_git.feature.definitions.GitBranchType:
        """
        If there are no branches, the git_repo_default_branch operation will
        return None, aka there si no default branch. Therefore, in this
        operation, we check if there are any branches at all, and if there are
        not we create a new branch. We could optionally facilitate interaction
        of multiple similar operations which wish to create a default branch if
        none exist by creating a new defintion which is locked which could be
        used to synchronise communication aka request for lock from some service
        which has no native locking (transmistion of NFT via DIDs over abitrary
        channels for example).
        """
        branches = (
            await dffml_feature_git.feature.operations.check_output(
                "git", "branch", "-r", cwd=repo.directory
            )
        ).split("\n")
        # If there's branches then bail out
        if list(filter(bool, branches)):
            return
        await dffml.run_command(
            ["git", "branch", "-M", name], cwd=repo.directory, logger=self.logger,
        )
        await dffml.run_command(
            ["git", "commit", "-m", "Created branch", "--allow-empty"],
            logger=self.logger,
        )
        return name
