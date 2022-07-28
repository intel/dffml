import pathlib
import textwrap
import itertools
from typing import NamedTuple, NewType, Optional


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
            ["git", "branch", "-M", name],
            cwd=repo.directory,
            logger=self.logger,
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
            remote, url_and_usages = (
                result.decode().strip().split("\t", maxsplit=2)
            )
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


# NOTE Not sure if the orchestrator will know what to do if we do this
# ReadmeGitRepo = AliceGitRepo
class ReadmeGitRepo(NamedTuple):
    directory: str
    URL: str


class OverlayREADME:
    ReadmePath = NewType("ReadmePath", object)
    ReadmeContents = NewType("repo.directory.readme.contents", str)
    ReadmeCommitMessage = NewType("repo.readme.git.commit.message", str)
    ReadmeBranch = NewType("repo.readme.git.branch", str)
    ReadmePR = NewType("ReadmePR", str)
    ReadmeIssue = NewType("ReadmeIssue", str)
    ReadmeIssueBody = NewType("ReadmeIssueBody", str)
    ReadmeIssueTitle = NewType("ReadmeIssueTitle", str)
    ReadmePRTitle = NewType("github.pr.title", str)
    ReadmePRBody = NewType("github.pr.body", str)

    # async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
    async def alice_contribute_readme(
        self, repo: AliceGitRepo
    ) -> ReadmeGitRepo:
        # TODO Clean this up once SystemContext refactor complete
        overlay_readme_dataflow = dffml.DataFlow(
            *itertools.chain(
                *[
                    dffml.object_to_operations(cls)
                    for cls in [
                        OverlayREADME,
                        *dffml.Overlay.load(
                            entrypoint="dffml.overlays.alice.please.contribute.recommended_community_standards.overlay.readme"
                        ),
                    ]
                ]
            )
        )
        async with dffml.run_dataflow.imp(
            # dataflow=self.octx.config.dataflow,
            dataflow=overlay_readme_dataflow,
            input_set_context_cls=AliceGitRepoInputSetContext,
        ) as custom_run_dataflow:
            # Copy all inputs from parent context into child. We eventually
            # should have InputNetworks which support acting as generic Copy on
            # Write over an underlying InputNetwork.
            async with custom_run_dataflow(
                self.ctx, self.octx
            ) as custom_run_dataflow_ctx:
                async with self.octx.ictx.definitions(self.ctx) as definitions:
                    custom_run_dataflow.config.dataflow.seed = (
                        custom_run_dataflow.config.dataflow.seed
                        + [
                            item
                            async for item in definitions.inputs()
                            if (
                                item.definition
                                in custom_run_dataflow.config.dataflow.definitions.values()
                                and item.definition
                                not in self.parent.op.inputs.values()
                            )
                        ]
                    )
                input_key = list(self.parent.op.inputs.keys())[0]
                key, definition = list(self.parent.op.outputs.items())[0]
                # This is the type cast
                custom_run_dataflow.op = custom_run_dataflow.op._replace(
                    # TODO Debug why the commented out version doesn't work
                    # Likely due to re-auto-definition
                    inputs={input_key: definition},
                    outputs={},
                )
                await dffml.run_dataflow.run_custom(
                    custom_run_dataflow_ctx,
                    {
                        input_key: dffml.Input(
                            value=repo,
                            definition=definition,
                            parents=None,
                            origin=(self.parent.op.instance_name, key),
                        )
                    },
                )

    # TODO Run this system context where readme contexts is given on CLI or
    # overriden via disabling of static overlay and application of overlay to
    # generate contents dynamiclly.
    # aka, test with `-inputs` option
    def create_readme_file_if_not_exists(
        self,
        repo: ReadmeGitRepo,
        readme_contents: Optional[
            "ReadmeContents"
        ] = "# My Awesome Project's README",
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
                    raise RuntimeError(
                        "Failed to create branch for contribution"
                    )
        await dffml.run_command(
            ["git", "add", "README.md"],
            cwd=repo.directory,
            logger=self.logger,
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
        title: Optional[
            "ReadmeIssueTitle"
        ] = "Recommended Community Standard: README",
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
    ) -> "ReadmeCommitMessage":
        return textwrap.dedent(
            f"""
            Recommended Community Standard: README

            Closes: {issue_url}
            """
        ).lstrip()

    @staticmethod
    async def readme_pr_body(readme_issue: "ReadmeIssue",) -> "ReadmePRBody":
        return f"Closes: {readme_issue}"

    async def readme_pr_title(
        self, readme_issue: "ReadmeIssue",
    ) -> "ReadmePRTitle":
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
                readme_issue,
            ],
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            if event is dffml.Subprocess.STDOUT:
                return result.strip().decode()


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
