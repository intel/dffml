import ast
import pathlib

from ..df.base import op
from ..df.types import Definition

from dffml_feature_git.feature.definitions import git_repository


@op(
    inputs={"repo": git_repository},
    outputs={
        "ast_tree": Definition(name="python.ast.tree", primitive="object"),
    },
    expand=["ast_tree"],
)
def parse_ast(repo):
    r"""
    Return AST objects for all Python files in a repo

    See https://asciinema.org/a/488667 for a recording of how this was written.

    Examples
    --------

    .. code-block::
        :test:

        $ dffml dataflow create \
            -- \
              check_if_valid_git_repository_URL \
              clone_git_repo \
              dffml.operation.python:parse_ast \
              cleanup_git_repo \
            | tee dataflow.json

    **repos.csv**

    .. code-block::
        :filepath: repos.csv

        name,source_url
        httptest,https://github.com/pdxjohnny/httptest

    .. code-block::
        :test:

        $ dffml list records \
            -sources preprocess=dfpreprocess \
            -source-preprocess-dataflow dataflow.json \
            -source-preprocess-record_def URL \
            -source-preprocess-source csv \
            -source-preprocess-source-filename repos.csv \
            -source-preprocess-source-key source_url

    .. code-block::
        :test:

        $ dffml dataflow diagram dataflow.json
    """
    return {
        "ast_tree": [
            ast.parse(path.read_text())
            for path in pathlib.Path(repo.directory).rglob("*.py")
        ],
    }
