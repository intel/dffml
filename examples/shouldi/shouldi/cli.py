# Command line utility helpers and DataFlow specific classes
from dffml import CMD, Arg, DataFlow, Input, GetSingle, run

# Import operations we need for the Git operations
from dffml_feature_git.feature.operations import (
    clone_git_repo,
    cleanup_git_repo,
)

# Import all the operations we wrote
from shouldi.bandit import run_bandit
from shouldi.pypi import pypi_latest_package_version
from shouldi.pypi import pypi_package_json
from shouldi.pypi import pypi_package_url
from shouldi.pypi import pypi_package_contents
from shouldi.pypi import cleanup_pypi_package
from shouldi.safety import safety_check
from shouldi.npm_audit import run_npm_audit

from dffml import op, Definition, run_dataflow

from typing import NamedTuple


class SAResultsSpec(NamedTuple):
    """
    Static analysis results for a language
    """

    critical: int
    high: int
    medium: int
    low: int
    report: dict


SA_RESULTS = Definition(
    name="static_analysis", primitive="string", spec=SAResultsSpec,
)


import pathlib


def has_file(directory: str, filename: str):
    return {"result": pathlib.Path(directory, filename).is_file()}


HAS_SETUP_PY_RESULT = Definition(name="has_setup_py_result", primitive="bool")


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={"result": HAS_SETUP_PY_RESULT},
)
def has_setup_py(repo: clone_git_repo.op.outputs["repo"].spec):
    return has_file(repo.directory, "setup.py")


HAS_PACKAGE_JSON_RESULT = Definition(
    name="has_package_json_result", primitive="bool"
)


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={"result": HAS_PACKAGE_JSON_RESULT},
)
def has_package_json(repo: clone_git_repo.op.outputs["repo"].spec):
    return has_file(repo.directory, "package.json")


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
async def is_lang_python(self, repo):
    async with self.octx.parent(DATAFLOW_ID_PYTHON) as octx:
        async for _, results in octx.run(
            [Input(value=repo, definition=self.parent.op.inputs["repo"])]
        ):
            if results[has_setup_py.op.outputs["result"].name]:
                return {"python": True}


# DataFlow for doing static analysis on Python code
DATAFLOW_SA_PYTHON = DataFlow.auto(
    pypi_package_json,
    pypi_latest_package_version,
    pypi_package_url,
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
DATAFLOW_SA_PYTHON.seed.append(
    Input(
        value=[
            safety_check.op.outputs["issues"].name,
            run_bandit.op.outputs["report"].name,
        ],
        definition=GetSingle.op.inputs["spec"],
    )
)


import os
from dffml import SetupPyKWArg


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={"result": SA_RESULTS},
    conditions=[is_lang_python.op.outputs["python"]],
)
async def run_python_sa(self, repo):
    """
    Run Python static analysis
    """
    setup_kwargs = SetupPyKWArg.get_kwargs(
        os.path.join(repo.directory, "setup.py")
    )

    # TODO Make is so that
    async with self.octx.parent(DATAFLOW_SA_PYTHON) as octx:
        async for _, results in octx.run(
            [
                Input(
                    value=setup_kwargs["name"],
                    definition=pypi_package_json.op.inputs["package"],
                )
            ]
        ):
            # TODO Make this report more useful
            safety_issues = results[safety_check.op.outputs["issues"].name]
            bandit_report = results[run_bandit.op.outputs["report"].name]
            return {
                "result": SAResultsSpec(
                    critical=safety_issues,
                    high=bandit_report["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"],
                    medium=0,
                    low=0,
                    report=results,
                )
            }


DATAFLOW_ID_JAVASCRIPT = DataFlow.auto(has_package_json, GetSingle)
DATAFLOW_ID_JAVASCRIPT.seed.append(
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
async def is_lang_javascript(self, repo):
    async with self.octx.parent(DATAFLOW_ID_JAVASCRIPT) as octx:
        async for _, results in octx.run(
            [Input(value=repo, definition=self.parent.op.inputs["repo"])]
        ):
            if results[has_package_json.op.outputs["result"].name]:
                return {"javascript": True}


DATAFLOW_SA_JAVASCRIPT = DataFlow.auto(run_npm_audit, GetSingle,)

DATAFLOW_SA_JAVASCRIPT.seed.append(
    Input(
        value=[run_npm_audit.op.outputs["report"].name,],
        definition=GetSingle.op.inputs["spec"],
    )
)


@op(
    inputs={"repo": clone_git_repo.op.outputs["repo"]},
    outputs={"result": SA_RESULTS},
    conditions=[is_lang_javascript.op.outputs["javascript"]],
)
async def run_javascript_sa(self, repo):
    """
    Run JS static analysis
    """

    # TODO Make is so that
    async with self.octx.parent(DATAFLOW_SA_JAVASCRIPT) as octx:
        async for _, results in octx.run(
            [
                Input(
                    value=repo.directory,
                    definition=run_npm_audit.op.inputs["pkg"],
                )
            ]
        ):
            # TODO Make this report more useful
            npm_report = results[run_npm_audit.op.outputs["report"].name]
            return {
                "result": SAResultsSpec(
                    critical=npm_report["critical"],
                    high=npm_report["high"],
                    medium=npm_report["moderate"],
                    low=npm_report["low"],
                    report=results,
                )
            }


# Link inputs and outputs together according to their definitions
DATAFLOW = DataFlow.auto(
    clone_git_repo,
    is_lang_python,
    run_python_sa,
    is_lang_javascript,
    run_javascript_sa,
    cleanup_git_repo,
    GetSingle,
)
DATAFLOW.seed.append(
    Input(value=[SA_RESULTS.name,], definition=GetSingle.op.inputs["spec"],)
)
for opimp in [
    is_lang_python,
    run_python_sa,
    is_lang_javascript,
    run_javascript_sa,
]:
    DATAFLOW.flow[opimp.op.name].inputs["repo"].append("seed")
DATAFLOW.update()


class Install(CMD):

    arg_packages = Arg(
        "packages", nargs="+", help="Package to check if we should install"
    )

    async def run(self):
        # Run all the operations, Each iteration of this loop happens
        # when all inputs are exhausted for a context, the output
        # operations are then run and their results are yielded
        async for package_name, results in run(
            DATAFLOW,
            {
                # For each package add a new input set to the input network
                # The context operations execute under is the package name
                # to evaluate. Contexts ensure that data pertaining to
                # package A doesn't mingle with data pertaining to package B
                package_name: [
                    # The only input to the operations is the package name.
                    Input(
                        value={
                            "URL": "file://"
                            + str(
                                pathlib.Path(package_name)
                                .expanduser()
                                .resolve()
                            ),
                            "directory": str(
                                pathlib.Path(package_name)
                                .expanduser()
                                .resolve()
                            ),
                        },
                        definition=clone_git_repo.op.outputs["repo"],
                    )
                    if pathlib.Path(package_name).is_dir()
                    else Input(
                        value=package_name,
                        definition=clone_git_repo.op.inputs["URL"],
                    )
                ]
                for package_name in self.packages
            },
        ):
            print(results)


class ShouldI(CMD):

    install = Install
