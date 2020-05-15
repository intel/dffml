import pathlib

from dffml import op, DataFlow, Input, Definition, GetSingle
from dffml_feature_git.feature.operations import clone_git_repo


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={
        "result": Definition(name="has_setup_py_result", primitive="bool")
    },
)
def has_setup_py(repo: clone_git_repo.op.outputs["repo"].spec):
    return {"result": pathlib.Path(repo.directory, "setup.py").is_file()}


DATAFLOW_ID_PYTHON = DataFlow.auto(has_setup_py, GetSingle)
DATAFLOW_ID_PYTHON.seed.append(
    Input(
        value=[has_setup_py.op.outputs["result"].name,],
        definition=GetSingle.op.inputs["spec"],
    )
)


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={"python": Definition(name="repo_is_python", primitive="string")},
)
async def check_python(self, repo):
    async with self.octx.parent(DATAFLOW_ID_PYTHON) as octx:
        async for _, results in octx.run(
            [Input(value=repo, definition=self.parent.op.inputs["repo"])]
        ):
            if results[has_setup_py.op.outputs["result"].name]:
                return {"python": True}
