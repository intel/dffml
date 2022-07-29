import pathlib
import textwrap
import itertools
from typing import NamedTuple, NewType, Optional, Type


import dffml
import dffml_feature_git.feature.definitions


class AliceGitRepo(NamedTuple):
    directory: str
    URL: str


class AliceGitRepoInputSetContextHandle(dffml.BaseContextHandle):
    def as_string(self) -> str:
        return str(self.ctx.repo)


class AliceGitRepoInputSetContext(dffml.BaseInputSetContext):
    def __init__(self, repo: AliceGitRepo):
        self.repo = repo

    async def handle(self) -> AliceGitRepoInputSetContextHandle:
        return AliceGitRepoInputSetContextHandle(self)

    def __repr__(self):
        return repr(self.repo)

    def __str__(self):
        return str(self.repo)


class AlicePleaseContributeRecommendedCommunityStandards:
    RepoString = NewType("repo.string", str)

    async def guess_repo_string_is_directory(
        repo_string: "RepoString",
    ) -> AliceGitRepo:
        # TODO(security) How bad is this?
        if not pathlib.Path(repo_string).is_dir():
            return
        return AliceGitRepo(directory=repo_string, URL=None)


# An overlay which could be installed if you have dffml-feature-git
# (aka dffml-operations-git) installed.
class OverlayGit:
    GuessedGitURL = NewType("guessed.git.url", bool)
    DefaultBranchName = NewType("default.branch.name", str)
    BaseBranch = NewType("repo.git.base.branch", str)
    WriteableGitRemoteOrigin = NewType("writable.github.remote.origin", str)

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

    # If you think you have a URL to a git repo, convert it so it will be
    # cloned.
    def guessed_repo_string_is_operations_git_url(
        repo_url: GuessedGitURL,
    ) -> dffml_feature_git.feature.definitions.URLType:
        return repo_url

    # If a Git repo was cloned, convert it to an AliceGitRepo so that Alice
    # know's she should be dealing with it.
    def git_repo_to_alice_git_repo(
        repo: dffml_feature_git.feature.definitions.git_repository,
    ) -> AliceGitRepo:
        return repo

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

    @staticmethod
    def determin_base_branch(
        default_branch: dffml_feature_git.feature.definitions.GitBranchType,
    ) -> "BaseBranch":
        # TODO .tools/process.yml which defines branches to contibute to under
        # different circumstances. Model with Linux kernel for complex case,
        # take KVM.
        # Later do NLP on contributing docs to determine
        return default_branch


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
                if event is dffml.Subprocess.STDOUT and result in (
                    "ADMIN",
                    "MAINTAIN",
                ):
                    return True
    return False


class OverlayGitHub:
    async def github_owns_remote(
        self,
        repo: AliceGitRepo,
        remote: dffml_feature_git.feature.definitions.git_remote,
    ) -> OverlayGit.WriteableGitRemoteOrigin:
        if repo.URL is None or not await github_owns_remote(
            self, repo.directory, remote, logger=self.logger
        ):
            return
        return remote
