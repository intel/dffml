from dffml import op, DataFlow, Input, GetSingle
from dffml_feature_git.feature.operations import clone_git_repo

from .npm_audit import run_npm_audit
from .check import check_javascript

from ..types import SA_RESULTS


DATAFLOW = DataFlow.auto(run_npm_audit, GetSingle,)
DATAFLOW.seed.append(
    Input(
        value=[run_npm_audit.op.outputs["report"].name,],
        definition=GetSingle.op.inputs["spec"],
    )
)


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={"result": SA_RESULTS},
    conditions=[check_javascript.op.outputs["javascript"]],
)
async def analyze_javascript(self, repo):
    """
    Run JS static analysis
    """

    async with self.octx.parent(DATAFLOW) as octx:
        async for _, results in octx.run(
            [
                Input(
                    value=repo.directory,
                    definition=run_npm_audit.op.inputs["pkg"],
                )
            ]
        ):
            npm_report = results[run_npm_audit.op.outputs["report"].name]
            return {
                "result": SA_RESULTS.spec(
                    critical=npm_report["critical"],
                    high=npm_report["high"],
                    medium=npm_report["moderate"],
                    low=npm_report["low"],
                    report=results,
                )
            }
