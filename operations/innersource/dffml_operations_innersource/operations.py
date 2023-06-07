import pathlib
import logging
import datetime
import itertools
from typing import List, NewType

import dffml
from dffml_feature_git.feature.definitions import (
    git_repository_checked_out,
    quarter_start_date,
)


GitHubActionsWorkflowUnixStylePath = NewType("GitHubActionsWorkflowUnixStylePath", str)
JenkinsfileWorkflowUnixStylePath = NewType("JenkinsfileWorkflowUnixStylePath", str)
GroovyFileWorkflowUnixStylePath = NewType("GroovyFileWorkflowUnixStylePath", str)
ActionYAMLFileWorkflowUnixStylePath = NewType("ActionYAMLFileWorkflowUnixStylePath", str)


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


@dffml.config
class MaintainedConfig:
    commits: int = dffml.field(
        "Equal or greater to this number of commits in the last quarter results in a return value of True",
        default=1,
    )


@dffml.op(
    inputs={
        "results": dffml.GroupBy.op.outputs["output"],
    },
    config_cls=MaintainedConfig,
    stage=dffml.Stage.OUTPUT,
)
def maintained(results: dict) -> bool:
    # As an example, if there is one commit in the last period (quarter), return
    # maintained (True for the maintained opreation for this input data).
    if results["commits"][-1] >= self.config_cls.commits:
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


RepoDirectory = NewType("RepoDirectory", str)


@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": RepoDirectory},
)
def repo_directory(self, repo: git_repository_checked_out.spec) -> RepoDirectory:
    # How did this not exist? I think it does somwhere else, another branch
    return {"result": repo.directory}


RepoURL = NewType("RepoURL", str)


@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": RepoURL},
)
def repo_url(self, repo: git_repository_checked_out.spec) -> RepoURL:
    """
    Helper opertion to expose repo URL of checked out repo object.

    TODO Remove this in favor of some kind of mapping extract style on objects
    ref engineering logs for more notes on @op.mapping.extract style decorator.
    """
    return {"result": repo.URL}


HasDocs = NewType("HasDocs", dict)


@dffml.op
def has_docs(
    repo_directory: RepoDirectory,
    readme_present: FileReadmePresent,
    *,
    logger: logging.Logger = None,
) -> HasDocs:
    # TODO Refactor this, ideally support regex and or open policy agent
    check_files_or_strings = ("support", "usage", "example", "known issues"),
    output = dict(zip(["readme_present", *check_files_or_strings], [False] * 5))
    for path in pathlib.Path(repo_directory).iterdir():
        if "readme" == path.stem.lower():
            output["readme_present"] = True
            for check in check_files_or_strings:
                if check in path.read_text().lower():
                    output[check] = True
        for check in check_files_or_strings:
            if check.replace(" ", "_") == path.stem.lower():
                output[check] = True
    return output
