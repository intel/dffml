r"""
.. note::

    To accept inputs coming from 'seed' origin with definition 'URL'

    .. code-block::

        [{"seed": ["URL"]}]'=repos:create_new_name.inputs.old_name \

.. code-block:: console

    $ dffml dataflow create \
        -configloader json \
        -flow \
          '[{"seed": ["URL"]}]'=dffml_feature_git.repos:create_new_name.inputs.old_name \
          '[{"repos:repos": "result"}]'=print_output.inputs.data \
        -inputs \
          'dffml'=github.owner \
          'False'=github.repo.public \
        -- \
          check_if_valid_git_repository_URL \
          clone_git_repo \
          git_repo_default_branch \
          dffml_feature_git.repos:create_new_name \
          dffml_feature_git.repos:push_to_github_new_repo \
          print_output \
        | tee "export.json"

.. code-block:: console

    $ dffml dataflow diagram export.json | tee mermaid.txt

https://mermaid-js.github.io/mermaid-live-editor/edit

.. code-block:: console

    $ dffml dataflow run records all \
        -inputs \
          true=no_git_branch_given \
        -log debug \
        -no-echo \
        -record-def URL \
        -dataflow "export.json" \
        -sources inputs=memory \
        -source-records \
          https://github.com/pdxjohnny/httptest \
          /home/pdxjohnny/Documents/python/active-directory-verifiable-credentials-python
"""
import shutil
import pathlib

import dffml
from dffml_feature_git.feature.definitions import (
    URL,
    git_repository,
    git_branch,
    GitRepoCheckedOutSpec,
)


@dffml.op
def create_new_name(old_name: str) -> str:
    return old_name.split("/")[-1]


@dffml.op(
    inputs={
        "old_name": URL,
        "repo": git_repository,
        "branch": git_branch,
        "new_name": create_new_name.op.outputs["result"],
        "owner": dffml.Definition(name="github.owner", primitive="str"),
        "public": dffml.Definition(
            name="github.repo.public", primitive="boolean"
        ),
    },
)
async def push_to_github_new_repo(
    self,
    old_name: str,
    repo: GitRepoCheckedOutSpec,
    branch: str,
    new_name: str,
    owner: str,
    public: bool,
) -> str:
    if "github.com" in repo.URL:
        # Fork if github
        await dffml.run_command(
            ["gh", "repo", "fork", "--org", owner,],
            logger=self.logger,
            cwd=repo.directory,
        )
    else:
        # Mirror otherwise
        # Run this only on condition that repo does not exist
        await dffml.run_command(
            [
                "gh",
                "repo",
                "create",
                "--public" if public else "--private",
                f"{owner}/{new_name}",
            ],
            logger=self.logger,
            cwd=repo.directory,
        )

        await dffml.run_command(
            [
                "git",
                "remote",
                "set-url",
                "origin",
                f"https://github.com/{owner}/{new_name}",
            ],
            cwd=repo.directory,
            logger=self.logger,
        )

        await dffml.run_command(
            ["git", "push", "-u", "origin", branch],
            cwd=repo.directory,
            logger=self.logger,
        )
