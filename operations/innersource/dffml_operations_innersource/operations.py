import pathlib
import datetime
from typing import List

import yaml

import dffml
from dffml_feature_git.feature.definitions import (
    git_repository,
    quarter_start_date,
)


@dffml.op(inputs={"repo": git_repository,},)
def github_workflow_present(repo: git_repository.spec) -> dict:
    return pathlib.Path(repo.directory, ".github", "workflows").is_dir()


# TODO Auto definition code which is about to undergo refactor will fix up this
# oddness with typing and half abilty to have auto inputs with types.
@dffml.op(inputs={}, outputs={"result": quarter_start_date})
def get_current_datetime_as_git_date():
    return {
        "result": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@dffml.op(inputs={"repo": git_repository,},)
def github_workflow_present(repo: git_repository.spec) -> dict:
    return pathlib.Path(repo.directory, ".github", "workflows").is_dir()


@dffml.op(stage=dffml.Stage.OUTPUT)
def maintained(results: dict) -> bool:
    return True


@dffml.config
class UnmaintainedConfig:
    commits: int = dffml.field(
        "Any less than this number of commits in the last quarter results in a return value of True",
        default=1,
    )


@dffml.op(
    stage=dffml.Stage.OUTPUT, config_cls=UnmaintainedConfig,
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


# --- DataFlow in same file for now, for convenience of viewing all in one we
#     will split later. ---

import sys

import dffml_feature_git.feature.operations

COLLECTOR_DATAFLOW = dffml.DataFlow(
    dffml.GroupBy,
    *dffml.opimp_in(dffml_feature_git.feature.operations),
    *dffml.opimp_in(sys.modules[__name__]),
)
COLLECTOR_DATAFLOW.seed = [
    dffml.Input(value=10, definition=COLLECTOR_DATAFLOW.definitions["quarters"]),
    dffml.Input(
        value=True, definition=COLLECTOR_DATAFLOW.definitions["no_git_branch_given"],
    ),
    dffml.Input(
        value={
            "authors": {"group": "author_count", "by": "quarter",},
            "commits": {"group": "commit_count", "by": "quarter",},
            "work": {"group": "work_spread", "by": "quarter",},
        },
        definition=COLLECTOR_DATAFLOW.definitions["group_by_spec"],
    ),
]


import copy
import dataclasses
import dffml.cli.dataflow


DEFAULT_SOURCE = dffml.JSONSource(
    filename=pathlib.Path(
        ".tools",
        "open-architecture",
        "innersource",
        "repos.json",
    ),
    readwrite=True,
    allowempty=True,
    mkdirs=True,
)


# NOTE When CLI and operations are merged: All this is the same stuff that will
# happen to Operation config_cls structures. We need a more ergonomic API to
# obsucre the complexity dataclasses introduces when modifying fields/defaults
# within subclasses.
for dffml_cli_class_name, field_modifications in {
    "RunAllRecords": {
        # metadata setting could be less awkward
        "dataflow": {"default": COLLECTOR_DATAFLOW},
        "record_def": {"default": COLLECTOR_DATAFLOW.definitions["URL"].name},
        "sources": {"default_factory": lambda: dffml.Sources(DEFAULT_SOURCE)}
    },
    "RunRecordSet": {
        "dataflow": {"default": COLLECTOR_DATAFLOW},
        "record_def": {"default": COLLECTOR_DATAFLOW.definitions["URL"].name},
        "sources": {"default_factory": lambda: dffml.Sources(DEFAULT_SOURCE)}
    },
    "Diagram": {"dataflow": {"default": COLLECTOR_DATAFLOW,},},
}.items():
    # Create the class and config names by prepending InnerSource
    inner_source_class_name = "InnerSource" + dffml_cli_class_name
    inner_source_class_config_name = inner_source_class_name + "Config"
    # Copy the old class
    inner_source_class_config = type(
        inner_source_class_config_name,
        (getattr(dffml.cli.dataflow, dffml_cli_class_name + "Config"),),
        {},
    )
    inner_source_class = type(
        inner_source_class_name,
        (getattr(dffml.cli.dataflow, dffml_cli_class_name),),
        {"CONFIG": inner_source_class_config,},
    )
    # Add our new class to the global namespace
    setattr(
        sys.modules[__name__],
        inner_source_class_config_name,
        inner_source_class_config,
    )
    setattr(
        sys.modules[__name__], inner_source_class_name, inner_source_class,
    )
    # Create mapping of fields
    fields = {
        field.name: field for field in dataclasses.fields(inner_source_class_config)
    }
    # Modify fields
    for field_name, modifications in field_modifications.items():
        if not field_name in fields:
            raise KeyError(field_name, fields)
        for key_to_modify, value_to_use in modifications.items():
            setattr(fields[field_name], key_to_modify, value_to_use)


class InnerSourceRunRecords(dffml.CMD):
    """Run DataFlow and assign output to a record"""

    _set = InnerSourceRunRecordSet
    _all = InnerSourceRunAllRecords


class InnerSourceRun(dffml.CMD):
    """Run dataflow"""

    records = InnerSourceRunRecords


class InnerSourceCLI(dffml.CMD):

    run = InnerSourceRun
    diagram = InnerSourceDiagram
