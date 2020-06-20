import pathlib

from dffml import op, DataFlow, Input, GetSingle, SetupPyKWArg
from dffml_feature_git.feature.operations import clone_git_repo

from ..types import SA_RESULTS

from .bandit import run_bandit
from .pypi import pypi_package_json
from .pypi import pypi_package_contents
from .pypi import cleanup_pypi_package
from .safety import safety_check
from .check import check_python

# DataFlow for doing static analysis on Python code
DATAFLOW = DataFlow.auto(
    pypi_package_json,
    pypi_package_contents,
    cleanup_pypi_package,
    safety_check,
    run_bandit,
    GetSingle,
)
# Seed inputs are added to each executing context. The following Input tells the
# GetSingle output operation that we want the output of the network to include
# data matching the "issues" output of the safety_check operation, and the
# "report" output of the run_bandit operation, for each context.
DATAFLOW.seed.append(
    Input(
        value=[
            safety_check.op.outputs["result"].name,
            run_bandit.op.outputs["result"].name,
        ],
        definition=GetSingle.op.inputs["spec"],
    )
)


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={"result": SA_RESULTS},
    conditions=[check_python.op.outputs["python"]],
)
async def analyze_python(self, repo):
    """
    Run Python static analysis
    """
    setup_kwargs = SetupPyKWArg.get_kwargs(
        str(pathlib.Path(repo.directory, "setup.py"))
    )
    async with self.octx.parent(DATAFLOW) as octx:
        async for _, results in octx.run(
            [
                Input(
                    value=setup_kwargs["name"],
                    definition=pypi_package_json.op.inputs["package"],
                )
            ]
        ):
            # TODO Make this report more useful
            safety_issues = results[safety_check.op.outputs["result"].name]
            bandit_report = results[run_bandit.op.outputs["result"].name]
            return {
                "result": SA_RESULTS.spec(
                    critical=safety_issues,
                    high=bandit_report["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"],
                    medium=bandit_report[
                        "CONFIDENCE.HIGH_AND_SEVERITY.MEDIUM"
                    ],
                    low=bandit_report["CONFIDENCE.HIGH_AND_SEVERITY.LOW"],
                    report=results,
                )
            }
