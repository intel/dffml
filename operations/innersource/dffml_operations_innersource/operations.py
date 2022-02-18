import pathlib
from typing import List

import yaml

from dffml.df.base import op
from dffml_feature_git.feature.definitions import git_repository


@op(
    inputs={
        "repo": git_repository,
    },
)
async def github_workflow_present(repo: git_repository.spec) -> dict:
    return bool(pathlib.Path(repo.directory, ".github", "workflows").is_dir())
