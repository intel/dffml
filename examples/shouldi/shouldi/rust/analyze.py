from dffml import op, DataFlow, Input, GetSingle
from dffml_feature_git.feature.operations import clone_git_repo

from .cargo_audit import run_cargo_audit
from .check import check_rust
from ..types import SA_RESULTS


DATAFLOW = DataFlow.auto(run_cargo_audit, GetSingle,)
DATAFLOW.seed.append(
    Input(
        value=[run_cargo_audit.op.outputs["report"].name,],
        definition=GetSingle.op.inputs["spec"],
    )
)


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={"result": SA_RESULTS},
    conditions=[check_rust.op.outputs["rust"]],
)
async def analyze_rust(self, repo):
    """
    Run Rust static analysis
    """

    async with self.octx.parent(DATAFLOW) as octx:
        async for _, results in octx.run(
            [
                Input(
                    value=repo.directory,
                    definition=run_cargo_audit.op.inputs["pkg"],
                )
            ]
        ):
            cargo_report = results[run_cargo_audit.op.outputs["report"].name]

            return {
                "result": SA_RESULTS.spec(
                    report=cargo_report, **cargo_report["qualitative"]
                )
            }
