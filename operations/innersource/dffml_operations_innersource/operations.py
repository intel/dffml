import pathlib
import datetime
from typing import List, NewType

import yaml

import dffml
from dffml_feature_git.feature.definitions import (
    git_repository_checked_out,
    quarter_start_date,
)


GitHubActionsWorkflowUnixStylePath = NewType("GitHubActionsWorkflowUnixStylePath", str)
JenkinsfileWorkflowUnixStylePath = NewType("JenkinsfileWorkflowUnixStylePath", str)
GroovyFileWorkflowUnixStylePath = NewType("GroovyFileWorkflowUnixStylePath", str)
ActionYAMLFileWorkflowUnixStylePath = NewType("ActionYAMLFileWorkflowUnixStylePath", str)

# Check for
#   "usage", "example(s)", "Known issues" (text or link to issue tracker) in docs
#   Support / contact information in docs (issue tracker link)
#   Linting (goovy linter, YAML linting), score it needs to meet
#   CI/CD on library itself (Actions workflows or webhooks configured)
#   We want to check for branch protection
#   We want to make sure that the issues are being addressed (hyptothetical SLA estimates)
#   Libraries should not have any hardcoded settings
#   Credentials must be managed securly and with minimal scope needed
#   Dependencies
#   - Must be explictly documented somewhere (SBOM okay)
#   - All dependnecies should be created by github or github verified createors or within dffml org
#   We should seperate seperate functionality into seperate libraries
#   We should be using symver


def relative_paths(
    directory: str,
    paths: List[str],
):
    return [
        path.relative_to(directory)
        for path in paths
    ]


@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": GitHubActionsWorkflowUnixStylePath},
    expand=["result"],
)
def github_workflows(self, repo: git_repository_checked_out.spec) -> dict:
    return {
        "result": map(
            str,
            relative_paths(
                repo.directory,
                pathlib.Path(repo.directory, ".github", "workflows").glob("*.yml"),
            ),
        ),
    }


@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": JenkinsfileWorkflowUnixStylePath},
    expand=["result"],
)
def jenkinsfiles(self, repo: git_repository_checked_out.spec) -> dict:
    return {
        "result": map(
            str,
            relative_paths(
                repo.directory,
                pathlib.Path(repo.directory).rglob("**/*Jenkinsfile")
            ),
        ),
    }


@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": GroovyFileWorkflowUnixStylePath},
    expand=["result"],
)
def groovy_files(self, repo: git_repository_checked_out.spec) -> dict:
    return {
        "result": map(
            str,
            relative_paths(
                repo.directory,
                [
                    *pathlib.Path(repo.directory).rglob("vars/*.groovy"),
                    *pathlib.Path(repo.directory).rglob("src/**/*.groovy"),
                ],
            ),
        ),
    }

@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": ActionYAMLFileWorkflowUnixStylePath},
    expand=["result"],
)
def action_yml_files(self, repo: git_repository_checked_out.spec) -> dict:
    return {
        "result": map(
            str,
            relative_paths(
                repo.directory,
                pathlib.Path(repo.directory).rglob("**/action.yml")
            ),
        ),
    }


FileReadmePresent = NewType("FileReadmePresent", bool)
FileContributingPresent = NewType("FileContributingPresent", bool)
FileCodeOfConductPresent = NewType("FileCodeOfConductPresent", bool)
FileSecurityPresent = NewType("FileSecurityPresent", bool)
FileSupportPresent = NewType("FileSupportPresent", bool)


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def readme_present(self, repo: git_repository_checked_out.spec) -> FileReadmePresent:
    return any(
        [
            path
            for path in pathlib.Path(repo.directory).iterdir()
            if "readme" == path.stem.lower()
        ]
    )


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def contributing_present(self, repo: git_repository_checked_out.spec) -> FileContributingPresent:
    return any(
        [
            pathlib.Path(repo.directory, "CONTRIBUTING.md").is_file(),
            pathlib.Path(repo.directory, "CONTRIBUTING.rst").is_file()
        ]
    )


# TODO Check compliance with RFC 9116
@dffml.op(inputs={"repo": git_repository_checked_out,},)
def security_present(self, repo: git_repository_checked_out.spec) -> FileSecurityPresent:
    return any(
        [
            pathlib.Path(repo.directory, "SECURITY.md").is_file(),
            pathlib.Path(repo.directory, "SECURITY.rst").is_file(),
            pathlib.Path(repo.directory, "SECURITY.txt").is_file(),
            pathlib.Path(repo.directory, "security.txt").is_file(),
        ]
    )


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def support_present(self, repo: git_repository_checked_out.spec) -> FileSupportPresent:
    return any(
        [
            pathlib.Path(repo.directory, "SUPPORT.md").is_file(),
            pathlib.Path(repo.directory, "SUPPORT.rst").is_file(),
        ]
    )


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def code_of_conduct_present(self, repo: git_repository_checked_out.spec) -> FileCodeOfConductPresent:
    return any(
        [
            pathlib.Path(repo.directory, "CODE_OF_CONDUCT.md").is_file(),
            pathlib.Path(repo.directory, "CODE_OF_CONDUCT.rst").is_file(),
        ]
    )


# TODO Auto definition code which is about to undergo refactor will fix up this
# oddness with typing and half abilty to have auto inputs with types.
@dffml.op(inputs={}, outputs={"result": quarter_start_date})
def get_current_datetime_as_git_date():
    return {
        "result": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@dffml.op(
    inputs={
        "results": dffml.GroupBy.op.outputs["output"],
    },
    stage=dffml.Stage.OUTPUT,
)
def maintained(results: dict) -> bool:
    return True


@dffml.config
class UnmaintainedConfig:
    commits: int = dffml.field(
        "Any less than this number of commits in the last quarter results in a return value of True",
        default=1,
    )


@dffml.op(
    inputs={
        "results": dffml.GroupBy.op.outputs["output"],
    },
    stage=dffml.Stage.OUTPUT,
    config_cls=UnmaintainedConfig,
)
def unmaintained(self, results: dict) -> bool:
    # As an example, if there are no commits in the last quarter, return
    # unmaintained (True for the unmaintained opreation for this input data).
    if results["commits"][-1] < self.config_cls.commits:
        return True


# TODO We may not need stage anymore, need to see if we should depricate
@dffml.op(
    stage=dffml.Stage.OUTPUT, conditions=[maintained.op.outputs["result"]],
)
def badge_maintained() -> str:
    return "https://img.shields.io/badge/Maintainance-Active-green"


@dffml.op(
    stage=dffml.Stage.OUTPUT, conditions=[unmaintained.op.outputs["result"]],
)
def badge_unmaintained() -> str:
    return "https://img.shields.io/badge/Maintainance-Inactive-red"
