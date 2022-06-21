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

    def has_readme(self, repo: AliceGitRepo,) -> "HasReadme":
        return pathlib.Path(repo.directory, "README.md").exists()

    # TODO Run this system context where readme contexts is given on CLI or
    # overriden via disabling of static overlay and application of overlay to
    # generate contents dynamiclly.
    def create_readme_file(
        self,
        repo: AliceGitRepo,
        has_readme: "HasReadme",
        readme_contents: Optional["ReadmeContents"] = "# My Awesome Project's README",
    ):
        # Do not create readme if it already exists
        if has_readme:
            return
        pathlib.Path(repo.directory, "README.md").write_text(readme_contents)


class AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:
    ReadmeCommitMessage = NewType("repo.readme.git.commit.message", str)
    ReadmeBranch = NewType("repo.readme.git.branch", str)
    BaseBranch = NewType("repo.git.base.branch", str)

    git_repo_default_branch = staticmethod(
        dffml_feature_git.feature.operations.git_repo_default_branch
    )

    @staticmethod
    def determin_base_branch(
        default_branch: dffml_feature_git.feature.definitions.git_branch,
    ) -> "BaseBranch":
        # TODO .tools/process.yml which defines branches to contibute to under
        # different circumstances. Model with Linux kernel for complex case,
        # take KVM.
        # Later do NLP on contributing docs to determine
        return default_branch

    @staticmethod
    async def contribute_readme_md(
        repo: AliceGitRepo,
        base: "BaseBranch",
        commit_message: Optional[
            "ReadmeCommitMessage"
        ] = "Recommended Community Standard: Add README",
    ) -> "ReadmeBranch":
        await dffml.run_command(
            ["git", "checkout", base,], cwd=repo.directory,
        )
        await dffml.run_command(
            [
                "git",
                "checkout",
                "-b",
                "alice-contribute-recommended-community-standards-readme",
            ],
            cwd=repo.directory,
        )
        await dffml.run_command(
            ["git", "add", "README.md",], cwd=repo.directory,
        )
        await dffml.run_command(
            ["git", "commit", "-sm", commit_message,], cwd=repo.directory,
        )


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

    ReadmePath = NewType("ReadmePath", str)
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
        ):
            if event is Subprocess.STDOUT:
                # The URL of the issue created
                return result.strip()

    @staticmethod
    def readme_commit_message(
        issue_url: "ReadmeIssue",
    ) -> AlicePleaseContributeRecommendedCommunityStandardsOverlayGit.ReadmeCommitMessage:
        return textwrap.dedent(
            f"""
            Recommended Community Standard: README

            Closes: #{issue_url}
            """
        ).lstrip()

    @staticmethod
    def meta_issue_body(
        repo: AliceGitRepo,
        readme_issue: Optional["ReadmeIssue"] = None,
        readme_path: Optional["ReadmePath"] = None,
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
                "- [x] [README]({repo.URL}/blob/{base}/{readme_path.relative_to(repo.directory).as_posix()})"
                if readme_path is not None
                else "- [ ] {readme_issue}",
            ]
        )

    @staticmethod
    async def create_meta_issue(
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
        ):
            if event is Subprocess.STDOUT:
                # The URL of the issue created
                return result.strip()


# TODO Spawn background task (could use an orchestrator which creates a
# GitHub Actions cron job to execute later). set_close_meta_issue_trigger
class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest:
    ReadmePR = NewType("ReadmePR", str)

    @staticmethod
    async def readme_pr(
        repo: AliceGitRepo,
        base: AlicePleaseContributeRecommendedCommunityStandardsOverlayGit.BaseBranch,
        head: AlicePleaseContributeRecommendedCommunityStandardsOverlayGit.ReadmeBranch,
    ) -> "ReadmePR":
        """

        Check if we have any other issues open for the repo

        .. code-block:: console
            :exec:

            $ gh issue -R "${GITHUB_REPO_URL}" create --title "Recommended Community Standards (alice)" --body "${META_ISSUE_BODY}"

        """
        await dffml.run_command(
            [
                "gh",
                "pr",
                "create",
                "--base",
                default_branch,
                "--head",
                head,
                "--body",
                body,
            ],
            cwd=repo.directory,
        )


class AlicePleaseContributeCLI(dffml.CMD):

    CONFIG = AlicePleaseContributeCLIConfig

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
            dffml.DataFlow(
                *itertools.chain(
                    *[
                        [
                            dffml.op(
                                name=f"{cls.__module__}.{cls.__qualname__}:{name}"
                            )(method)
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
                            AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI,
                            AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue,
                            AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest,
                        ]
                    ]
                )
            ),
            [dffml.Input(value=self, definition=DFFMLCLICMD,),],
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
