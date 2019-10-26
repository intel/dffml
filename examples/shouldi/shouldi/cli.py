# Command line interface helpers
from dffml.util.cli.cmd import CMD
from dffml.util.cli.arg import Arg

# DataFlow specific classes
from dffml.df.types import DataFlow, Input
from dffml.df.memory import MemoryOrchestrator

# The GetSingle operation will grab the data we want from the ouputs of our
# operations and present it as the result
from dffml.operation.output import GetSingle

# Import all the operations we wrote
from shouldi.bandit import run_bandit
from shouldi.pypi import pypi_latest_package_version
from shouldi.pypi import pypi_package_json
from shouldi.pypi import pypi_package_url
from shouldi.pypi import pypi_package_contents
from shouldi.pypi import cleanup_pypi_package
from shouldi.safety import safety_check

# Link inputs and outputs together according to their definitions
DATAFLOW = DataFlow.auto(
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
DATAFLOW.seed.append(
    Input(
        value=[
            safety_check.op.outputs["issues"].name,
            run_bandit.op.outputs["report"].name,
        ],
        definition=GetSingle.op.inputs["spec"],
    )
)


class Install(CMD):

    arg_packages = Arg(
        "packages", nargs="+", help="Package to check if we should install"
    )

    async def run(self):
        # Create an Orchestrator which will manage the running of our operations
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            # Create a orchestrator context, everything in DFFML follows this
            # one-two context entry pattern
            async with orchestrator(DATAFLOW) as octx:
                # Run all the operations, Each iteration of this loop happens
                # when all inputs are exhausted for a context, the output
                # operations are then run and their results are yielded
                async for package_name, results in octx.run(
                    {
                        # For each package add a new input set to the input network
                        # The context operations execute under is the package name
                        # to evaluate. Contexts ensure that data pertaining to
                        # package A doesn't mingle with data pertaining to package B
                        package_name: [
                            # The only input to the operations is the package name.
                            Input(
                                value=package_name,
                                definition=pypi_package_json.op.inputs[
                                    "package"
                                ],
                            )
                        ]
                        for package_name in self.packages
                    }
                ):
                    # Grab the number of safety issues and the bandit report
                    # from the results dict
                    safety_issues = results[
                        safety_check.op.outputs["issues"].name
                    ]
                    bandit_report = results[
                        run_bandit.op.outputs["report"].name
                    ]
                    # Decide if those numbers mean we should stop ship or not
                    if (
                        safety_issues > 0
                        or bandit_report["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"]
                        > 5
                    ):
                        print(f"Do not install {package_name}!")
                        for definition_name, result in results.items():
                            print(f"    {definition_name}: {result}")
                    else:
                        print(f"{package_name} is okay to install")


class ShouldI(CMD):

    install = Install
