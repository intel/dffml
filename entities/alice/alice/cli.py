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
import shouldi.cli
import dffml_operations_innersource.cli

from .system_context import Alice
from .threats_md import THREATS_MD_DATAFLOW


class AliceGitRepo(NamedTuple):
    directory: str
    URL: str


DFFMLCLICMD = NewType("dffml.util.cli.CMD", object)


# NOTE When CLI and operations are merged: All this is the same stuff that will
# happen to Operation config_cls structures. We need a more ergonomic API to
# obsucre the complexity dataclasses introduces when modifying fields/defaults
# within subclasses.
for dffml_cli_class_name, field_modifications in {
    "RunSingle": {
        "dataflow": {"default_factory": lambda: THREATS_MD_DATAFLOW},
        "no_echo": {"default": True},
    },
}.items():
    # Create the class and config names by prepending InnerSource
    new_class_name = "AliceThreatsMd"
    # Create a derived class
    new_class = getattr(dffml.cli.dataflow, dffml_cli_class_name).subclass(
        new_class_name, field_modifications,
    )
    # Add our new class to the global namespace
    setattr(
        sys.modules[__name__], new_class.CONFIG.__qualname__, new_class.CONFIG,
    )
    setattr(
        sys.modules[__name__], new_class.__qualname__, new_class,
    )


class ShouldiCLI(dffml.CMD):

    # TODO Overlay dataflow so that upstream shouldi install is used as part of
    # our python package evauation
    # TODO Take PURL or SW Heritage ID as an input definition
    use = shouldi.cli.ShouldI.install
    reuse = shouldi.use.Use
    contribute = dffml_operations_innersource.cli.InnerSourceCLI.run.records._set
    # diagram = ShouldiDiagram


class AliceProduceCLI(dffml.CMD):

    sbom = shouldi.project.cli.ProjectCMD.create


class AliceCLI(dffml.CMD):

    produce = AliceProduceCLI


@dffml.config
class AlicePleaseContributeCLIConfig:
    repos: List[str] = dffml.field(
        "Repos to contribute to", default_factory=lambda: [],
    )


import dffml_feature_git.feature.definitions


# TODO GitRepoSpec resolve to correct definition on auto def
class AlicePleaseContributeRecommendedCommunityStandards:
    # TODO SystemContext __new__ auto populate config to have upstream set to
    # dataflow generated from methods in this class with memory orchestarator.
    ReadmePath = NewType("ReadmePath", object)
    RepoString = NewType("repo.string", str)
    ReadmeContents = NewType("repo.directory.readme.contents", str)
    HasReadme = NewType("repo.directory.readme.exists", bool)

    # TODO Generate output definition when wrapped with op decorator, example:
    #   HasReadme = NewType("AlicePleaseContributeRecommendedCommunityStandards.has.readme", bool)

    # TODO
    # ) -> bool:
    # ...
    #     has_readme: 'has_readme',

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


AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI = NewType(
    "AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI", bool
)

import dffml.df.types

# TODO A way to deactivate installed overlays so they are not merged or applied.
class AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:
    CLIRunOnRepo = NewType("CLIRunOnRepo", str)

    @staticmethod
    def cli_is_asking_for_recommended_community_standards(
        cmd: DFFMLCLICMD,
    ) -> AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI:
        """

        .. code-block:: console
            :test:

            $ alice please contribute recommended community standards


        """
        if not "" in cmd.extra_config:
            return
        args = cmd.extra_config[""]["plugin"]
        if not isinstance(args, list):
            return
        return "recommended community standards" in " ".join(args)

    async def cli_is_meant_on_this_repo(
        self,
        cmd: DFFMLCLICMD,
        wanted: AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI,
    ) -> AsyncIterator["CLIRunOnRepo"]:
        if not wanted or cmd.repos:
            return
        yield os.getcwd()

    @staticmethod
    async def cli_has_repos(
        cmd: DFFMLCLICMD,
        wanted: AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI,
    ) -> AsyncIterator["CLIRunOnRepo"]:
        if not wanted:
            return
        # TODO directory should really be None
        for repo in cmd.repos:
            yield repo

    async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
        # TODO Similar to Expand being an alias of Union
        #
        # async def cli_run_on_repo(self, repo: 'CLIRunOnRepo') -> SystemContext[StringInputSetContext[AliceGitRepo]]:
        #     return repo
        #
        # Or ideally at class scope
        #
        # 'CLIRunOnRepo' -> SystemContext[StringInputSetContext[AliceGitRepo]]
        async with self.parent.__class__(self.parent.config) as custom_run_dataflow:
            async with custom_run_dataflow(
                self.ctx, self.octx
            ) as custom_run_dataflow_ctx:
                # This is the type cast
                custom_run_dataflow.op = self.parent.op._replace(
                    inputs={
                        "repo": AlicePleaseContributeRecommendedCommunityStandards.RepoString
                    }
                )
                # Set the dataflow to be the same flow
                # TODO Reuse ictx? Is that applicable?
                custom_run_dataflow.config.dataflow = self.octx.config.dataflow
                await dffml.run_dataflow.run_custom(
                    custom_run_dataflow_ctx, {"repo": repo},
                )


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
            ["git", "push", "-fu", origin, head], cwd=repo.directory, logger=self.logger,
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


class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubWritableRemotesFromPermissions:
    async def already_owns_repo(
        self, repo: AliceGitRepo,
    ) -> AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest.WriteableGitRemoteOrigin:
        if repo.URL is None:
            return
        origins = {}
        async for event, result in dffml.run_command_events(
            ["git", "remote", "-v"],
            cwd=repo.directory,
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT_READLINE],
        ):
            if event is dffml.Subprocess.STDOUT_READLINE:
                origin, url_and_usages = result.decode().strip().split("\t", maxsplit=2)
                origins[origin] = url_and_usages.split()[0]
        for origin, url in origins.items():
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
                logger=self.logger,
                events=[dffml.Subprocess.STDOUT],
            ):
                result = result.strip().decode()
                if event is dffml.Subprocess.STDOUT and result in (
                    "ADMIN",
                    "MAINTAIN",
                ):
                    return origin


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


# TODO(alice) Replace with definition as system context
AlicePleaseContributeCLIDataFlow = dffml.DataFlow(
    *itertools.chain(
        *[
            [
                dffml.op(name=f"{cls.__module__}.{cls.__qualname__}:{name}")(method)
                if not hasattr(method, "imp")
                else method.imp
                for name, method in inspect.getmembers(
                    cls,
                    predicate=lambda i: inspect.ismethod(i)
                    or inspect.isfunction(i)
                    and not hasattr(i, "__supertype__"),
                )
            ]
            for cls in [
                AlicePleaseContributeRecommendedCommunityStandards,
                AlicePleaseContributeRecommendedCommunityStandardsOverlayGit,
                AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit,
                AlicePleaseContributeRecommendedCommunityStandardsOverlayAliceOperationsGit,
                AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI,
                AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue,
                AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest,
                AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequestReferenceIssue,
                AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubWritableRemotesFromPermissions,
            ]
        ]
    )
)


class AlicePleaseContributeCLI(dffml.CMD):

    CONFIG = AlicePleaseContributeCLIConfig
    DATAFLOW = AlicePleaseContributeCLIDataFlow

    async def run(self):
        # TODO When running Alice from the CLI we will inspect the top level
        # system context in the furture applied overlay which is the alice
        # please contribute overlay which provides CLI applications. It should
        # auto populate the input required to the base repo dataflow.
        content_should_be = textwrap.dedent(
            """
            - [] [README](https://github.com/intel/dffml/blob/main/README.md)
            - [] Code of conduct
            - [] [Contributing](https://github.com/intel/dffml/blob/main/CONTRIBUTING.md)
            - [] [License](https://github.com/intel/dffml/blob/main/LICENSE)
            - [] Security
            """
        ).lstrip()

        # TODO Use overlays instead of combining all classes into one
        # TODO(alice) ctx is the system context, so it will have an orchestartor
        # property on it with the orchestrator which is yielding these results.
        async for ctx, results in dffml.run(
            self.DATAFLOW, [dffml.Input(value=self, definition=DFFMLCLICMD,),],
        ):
            print((await ctx.handle()).as_string(), results)

        return

        async for ctx, results in dffml.run(
            AlicePleaseContributeRecommendedCommunityStandards,
            # dffml.DataFlow(*dffml.opimp_in(locals())),
            [dffml.Input(value=self, definition=DFFMLCLICMD,),],
            # TODO Merge all overlays into one and then run
            overlay=AlicePleaseContributeRecommendedCommunityStandardsCLIOverlay,
        ):
            (await ctx.handle()).as_string()

        content_was = textwrap.dedent(
            """
            - [] [README](https://github.com/intel/dffml/blob/main/README.md)
            - [] Code of conduct
            - [] [Contributing](https://github.com/intel/dffml/blob/main/CONTRIBUTING.md)
            - [] [License](https://github.com/intel/dffml/blob/main/LICENSE)
            - [] Security
            """
        ).lstrip()

        unittest.TestCase().assertEqual(content_should_be, content_was)

        # TODO Implement creation of issues once we have body text generation
        # working.


class AlicePleaseCLI(dffml.CMD):

    contribute = AlicePleaseContributeCLI


class AliceCLI(dffml.CMD):

    shouldi = ShouldiCLI
    threats = AliceThreatsMd
    please = AlicePleaseCLI
    # TODO 2022-05-26 13:15 PM PDT: Maybe this should be a dataflow rather than
    # a system context? Or support both more likely.
    # version = DataFlow(op(stage=Stage.OUTPUT)(get_alice_version))
    # TODO Set parent as Input when runing and after overlay!!!
    # parent=None,
    # inputs=[]
    # architecture=OpenArchitecture(dataflow=DataFlow(op(stage=Stage.OUTPUT)(get_alice_version))),
    # orchestrator=MemoryOrchestrator(),
    # If we want results to be AliceVersion. Then we need to run the
    # operation which produces AliceVersion as an output operation.
    #
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO 2022-05-26 12:53 PM PDT  TODO TODO TODO
    # TODO TODO TODO        SEE BELOW         TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    #
    # THE TODO: We want grab SemanticVersion. Look for types who's liniage
    # is derived from that. If there is no operation which outputs a derived
    # or direct type. Raise invalid.
    #
    # We will overlay output operations and check validity
    #
    # For a system context to be used as a CLI command we will overlay with
    # an output operation which returns a single result within
    # dffml.util.cli.cmd. This flow should produce a result of the CLI
    # result data type. This flow should have an operation in it which
    # produces cli_result via taking a single peice of data derived from
    # SemanticVersion.
    #
    # We can check if we can use the System Context as a CLI command by
    # checking if it's valid when we overlay a system context which has an
    # the following input in it: `cli_result`. If we are we get an invalid
    # context, we know that we cannot use this as a CLI command, since it
    # doesn't produce a CLI result.
    #
    # Maybe we know that all CLI commands must accept an input int
    # architecture=OpenArchitecture(dataflow=DataFlow(op(stage=Stage.OUTPUT)(get_alice_version))),
    # version = Alice.only("version")
