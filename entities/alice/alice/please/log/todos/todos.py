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
from typing import NamedTuple, NewType, Optional, Type, AsyncIterator, Dict


import dffml
import dffml_feature_git.feature.definitions
import dffml_operations_innersource.operations


from ...contribute.recommended_community_standards.recommended_community_standards import AliceGitRepo
from ...contribute.util.gh import gh_issue_create


GitRepoCheckedOutSpecType = NewType(
    dffml_feature_git.feature.definitions.git_repository_checked_out.name,
    dffml_feature_git.feature.definitions.git_repository_checked_out.spec,
)


class AlicePleaseLogTodosDataFlow:
    RepoString = NewType("repo.string", str)
    GuessedGitURL = NewType("guessed.git.url", bool)

    # The operations we use defined elsewhere
    check_if_valid_git_repository_URL = (
        dffml_feature_git.feature.operations.check_if_valid_git_repository_URL
    )
    clone_git_repo = dffml_feature_git.feature.operations.clone_git_repo
    contributing_present = dffml_operations_innersource.operations.contributing_present
    security_present = dffml_operations_innersource.operations.security_present
    support_present = dffml_operations_innersource.operations.support_present
    code_of_conduct_present = dffml_operations_innersource.operations.code_of_conduct_present

    def guess_repo_string_is_url(
        self,
        repo_string: RepoString,
    ) -> GuessedGitURL:
        if "://" not in repo_string:
            return
        return repo_string

    # If you think you have a URL to a git repo, convert it so it will be
    # cloned.
    def guessed_repo_string_is_operations_git_url(
        repo_url: GuessedGitURL,
    ) -> dffml_feature_git.feature.definitions.URLType:
        return repo_url

    @dffml.op(
        # name="alice.please.log.todos.todos:AlicePleaseLogTodosDataFlow.git_repo_to_git_repository_checked_out",
        inputs={"repo": dffml_feature_git.feature.definitions.git_repository},
        outputs={"repo": dffml_feature_git.feature.definitions.git_repository_checked_out},
    )
    async def git_repo_to_git_repository_checked_out(
        self, repo: dffml_feature_git.feature.definitions.git_repository,
    ) -> dffml_feature_git.feature.definitions.git_repository_checked_out.spec:
        # We are not trying to look back in time with this stuff, so we just
        # need to convert the repo to an instance of a checked out repo to
        # trigger the checks for the various files to run.
        async for event, result in dffml.run_command_events(
            ["git", "log", "-n", "1", "--format=%H"],
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT],
        ):
            return {
                "repo": dffml_feature_git.feature.definitions.git_repository_checked_out.spec(
                    directory=repo.directory,
                    URL=repo.URL,
                    commit=result.strip().decode(),
                )
            }


class OverlayCLI:
    DFFMLCLICMD = NewType("dffml.util.cli.CMD", object)
    CLIRunOnRepo = NewType("CLIRunOnRepo", str)

    def cli_is_meant_on_this_repo(
        self,
        cmd: DFFMLCLICMD,
    ) -> "CLIRunOnRepo":
        if cmd.repos:
            return
        return os.getcwd()

    async def cli_has_repos(
        cmd: DFFMLCLICMD,
    ) -> AsyncIterator["CLIRunOnRepo"]:
        for repo in cmd.repos:
            yield repo

    async def cli_run_on_repo(
        self, repo: "CLIRunOnRepo"
    ) -> AlicePleaseLogTodosDataFlow.RepoString:
        # TODO This is copy paste from recommended_community_standards/cli.py
        # It needs refactoring, probably into the system context as class stuff.
        overlay_cli_dataflow = dffml.DataFlow(
            *itertools.chain(
                *[
                    dffml.object_to_operations(cls)
                    for cls in [
                        OverlayCLI,
                        *dffml.Overlay.load(
                            entrypoint="dffml.overlays.alice.please.log.todos.overlay.cli"
                        ),
                    ]
                ]
            )
        )
        # TODO copy.deepcopy(self.octx.config.dataflow)?
        async with dffml.run_dataflow.imp(
            dataflow=copy.deepcopy(self.octx.config.dataflow),
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
                                not in overlay_cli_dataflow.definitions.values()
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


# : dffml_operations_innersource.operations.FileReadmePresent
# : dffml_operations_innersource.operations.FileContributingPresent,
# : dffml_operations_innersource.operations.FileCodeOfConductPresent,
# : dffml_operations_innersource.operations.FileSecurityPresent,
class AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues:
    SupportIssueURL = NewType("SupportIssueURL", str)

    DEFAULT_SUPPORT_ISSUE_TITLE: str = "Recommended Community Standard: SUPPORT"
    DEFAULT_SUPPORT_ISSUE_BODY: str = "References:\n- https://docs.github.com/articles/about-supports/"

    # TODO(188) Unify Definition.spec and NewType (git_repository_checked_out).
    # Unification should result in dropping the @op decorator, auto defined
    # op inputs/outputs will fully operational when unification is complete.
    @dffml.op(
        inputs={
            "repo": dffml_feature_git.feature.definitions.git_repository_checked_out,
            "file_present": dffml_operations_innersource.operations.FileSupportPresent,
            "title": dffml.Definition(name="SupportIssueTitle", primitive="string", default=DEFAULT_SUPPORT_ISSUE_TITLE),
            "body": dffml.Definition(name="SupportIssueBody", primitive="string", default=DEFAULT_SUPPORT_ISSUE_BODY),
        },
        outputs={
            "issue_url": SupportIssueURL,
        },
    )
    async def gh_issue_create_support(
        self,
        repo: dffml_feature_git.feature.definitions.git_repository_checked_out.spec,
        file_present: dffml_operations_innersource.operations.FileSupportPresent,
        title,
        body,
    ) -> SupportIssueURL:
        if file_present:
            return
        return {
            "issue_url": await gh_issue_create(
                repo.URL,
                title,
                body,
                logger=self.logger,
            )
        }
