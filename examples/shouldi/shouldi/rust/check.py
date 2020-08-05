import pathlib

from dffml import op, DataFlow, Input, Definition, GetSingle
from dffml_feature_git.feature.operations import clone_git_repo


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={
        "result": Definition(name="has_package_cargo_result", primitive="bool")
    },
)
def has_package_cargo(repo: clone_git_repo.op.outputs["repo"].spec):
    return {
        "result": pathlib.Path(repo.directory, "cargo.toml").is_file()
        or pathlib.Path(repo.directory, "Cargo.toml").is_file()
    }


DATAFLOW = DataFlow.auto(has_package_cargo, GetSingle)
DATAFLOW.seed.append(
    Input(
        value=[has_package_cargo.op.outputs["result"].name,],
        definition=GetSingle.op.inputs["spec"],
    )
)


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={"rust": Definition(name="repo_is_rust", primitive="string")},
)
async def check_rust(self, repo):
    async with self.octx.parent(DATAFLOW) as octx:
        async for _, results in octx.run(
            [Input(value=repo, definition=self.parent.op.inputs["repo"])]
        ):
            if results[has_package_cargo.op.outputs["result"].name]:
                return {"rust": True}
