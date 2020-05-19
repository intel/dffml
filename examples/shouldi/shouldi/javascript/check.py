import pathlib

from dffml import op, DataFlow, Input, Definition, GetSingle
from dffml_feature_git.feature.operations import clone_git_repo


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={
        "result": Definition(name="has_package_json_result", primitive="bool")
    },
)
def has_package_json(repo: clone_git_repo.op.outputs["repo"].spec):
    return {"result": pathlib.Path(repo.directory, "package.json").is_file()}


DATAFLOW = DataFlow.auto(has_package_json, GetSingle)
DATAFLOW.seed.append(
    Input(
        value=[has_package_json.op.outputs["result"].name,],
        definition=GetSingle.op.inputs["spec"],
    )
)


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={
        "javascript": Definition(name="repo_is_javascript", primitive="string")
    },
)
async def check_javascript(self, repo):
    async with self.octx.parent(DATAFLOW) as octx:
        async for _, results in octx.run(
            [Input(value=repo, definition=self.parent.op.inputs["repo"])]
        ):
            if results[has_package_json.op.outputs["result"].name]:
                return {"javascript": True}
