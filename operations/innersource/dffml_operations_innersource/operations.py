import pathlib
import datetime
from typing import List

import yaml

import dffml
from dffml_feature_git.feature.definitions import (
    git_repository_checked_out,
    quarter_start_date,
)


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def github_workflow_present(self, repo: git_repository_checked_out.spec) -> dict:
    self.logger.debug("%s", list(pathlib.Path(repo.directory).rglob("*")))
    return pathlib.Path(repo.directory, ".github", "workflows").is_dir()


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def contributing_present(self, repo: git_repository_checked_out.spec) -> dict:
    return any(
        [
            pathlib.Path(repo.directory, "CONTRIBUTING.md").is_file(),
            pathlib.Path(repo.directory, "CONTRIBUTING.rst").is_file()
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
