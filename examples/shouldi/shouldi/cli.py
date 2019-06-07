import sys

from dffml.util.cli.cmd import CMD
from dffml.util.cli.arg import Arg

from dffml.df.types import Input
from dffml.df.base import (
    operation_in,
    opimp_in,
    Operation,
    BaseConfig,
    StringInputSetContext,
)
from dffml.df.memory import (
    MemoryOrchestrator,
    MemoryInputSet,
    MemoryInputSetConfig,
)
from dffml.operation.output import GetSingle

from shouldi.pypi import pypi_latest_package_version
from shouldi.safety import safety_check

OPERATIONS = operation_in(sys.modules[__name__])
OPIMPS = opimp_in(sys.modules[__name__])


class Install(CMD):

    arg_packages = Arg(
        "packages", nargs="+", help="Package to check if we should install"
    )

    async def run(self):
        async with MemoryOrchestrator.basic_config(
            operations=OPERATIONS,
            opimps={
                imp.op.name: imp
                for imp in [Imp(BaseConfig()) for Imp in OPIMPS]
            },
        ) as orchestrator:

            definitions = Operation.definitions(*OPERATIONS)

            packages = {
                package_name: Input(
                    value=package_name,
                    definition=definitions["package"],
                    parents=False,
                )
                for package_name in self.packages
            }

            get_single_spec = Input(
                value=["safety_check_number_of_issues"],
                definition=definitions["get_single_spec"],
                parents=False,
            )

            async with orchestrator() as octx:
                # Add our inputs to the input network with the context being the URL
                for package_name in packages.keys():
                    await octx.ictx.add(
                        MemoryInputSet(
                            MemoryInputSetConfig(
                                ctx=StringInputSetContext(package_name),
                                inputs=[packages[package_name]]
                                + [get_single_spec],
                            )
                        )
                    )

                async for ctx, results in octx.run_operations(strict=True):
                    package_name = (await ctx.handle()).as_string()
                    results = results["get_single"]
                    any_issues = any(map(bool, results.values()))
                    if any_issues:
                        print(f"Do not install {package_name}! {results!r}")
                    else:
                        print(f"{package_name} is okay to install")


class ShouldI(CMD):

    install = Install
