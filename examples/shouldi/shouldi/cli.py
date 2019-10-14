import sys

from dffml.df.types import Input, Operation, DataFlow, InputFlow
from dffml.df.base import operation_in, opimp_in
from dffml.df.memory import MemoryOrchestrator
from dffml.df.linker import Linker
from dffml.operation.output import GetSingle
from dffml.util.cli.cmd import CMD
from dffml.util.cli.arg import Arg

from shouldi.bandit import run_bandit
from shouldi.pypi import pypi_latest_package_version
from shouldi.pypi import pypi_package_json
from shouldi.pypi import pypi_package_url
from shouldi.pypi import pypi_package_contents
from shouldi.pypi import cleanup_pypi_package
from shouldi.safety import safety_check

# sys.modules[__name__] is a list of everything we've imported in this file.
# opimp_in returns a subset of that list, any OperationImplementations
OPIMPS = opimp_in(sys.modules[__name__])

# TODO(arv1ndh) Add the auto method to DataFlow
DATAFLOW = DataFlow(
    # The keys in the operations dict are the names of the instances of these
    # operations. This is needed because two of the same operation could be
    # instantiated with different configs.
    operations={
        "pkg.json": pypi_package_json,
        "pkg.version": pypi_latest_package_version,
        "pkg.url": pypi_package_url,
        "pkg.contents": pypi_package_contents,
        "pkg.cleanup": cleanup_pypi_package,
        "bandit": run_bandit,
        "safety": safety_check,
        "output": GetSingle,
    },
    # The flow defines how data will move between operation instances. For the
    # input of each operation, we specify where it will come from. The origin
    # could be a seed value to the network (a reserved word) or it could be in
    # the format of instance_name.output_parameter. We define a list of places
    # it could come from to ensure data could come from varying operations.
    flow={
        "pkg.json": InputFlow(package=["seed"]),
        "pkg.version": InputFlow(response_json=["pkg.json.response_json"]),
        "pkg.url": InputFlow(response_json=["pkg.json.response_json"]),
        "pkg.contents": InputFlow(url=["pkg.url.url"]),
        "pkg.cleanup": InputFlow(directory=["pkg.contents.directory"]),
        "bandit": InputFlow(pkg=["pkg.contents.directory"]),
        "safety": InputFlow(package=["seed"], version=["pkg.version.version"]),
    },
)


class Install(CMD):

    arg_packages = Arg(
        "packages", nargs="+", help="Package to check if we should install"
    )

    async def run(self):
        # Create an Orchestrator which will manage the running of our operations
        async with MemoryOrchestrator.basic_config() as orchestrator:
            # Create a orchestrator context, everything in DFFML follows this
            # one-two context entry pattern
            async with orchestrator() as octx:
                # Load the operations into the orchestrator context
                await octx.initialize_dataflow(DATAFLOW)
                # For each package add a new input set to the network of inputs
                # (ictx). Operations run under a context, the context here is
                # the package_name to evaluate (the first argument). The next
                # arguments are all the inputs we're seeding the network with
                # for that context. We give the package name because
                # pypi_latest_package_version needs it to find the version,
                # which safety will then use. We also give an input to the
                # output operation GetSingle, which takes a list of data type
                # definitions we want to select as our results.
                for package_name in self.packages:
                    await octx.ictx.sadd(
                        package_name,
                        Input(
                            value=package_name,
                            definition=pypi_package_json.op.inputs["package"],
                        ),
                        Input(
                            value=[
                                safety_check.op.outputs["issues"].name,
                                run_bandit.op.outputs["report"].name,
                            ],
                            definition=GetSingle.op.inputs["spec"],
                        ),
                    )

                # Run all the operations, Each iteration of this loop happens
                # when all inputs are exhausted for a context, the output
                # operations are then run and their results are yielded
                async for package_name, results in octx.run_operations():
                    # Grab the number of saftey issues and the bandit report
                    # from the results dict
                    safety_issues = results[
                        safety_check.op.outputs["issues"].name
                    ]
                    bandit_report = results[
                        run_bandit.op.outputs["report"].name
                    ]
                    if (
                        safety_issues > 0
                        or bandit_report["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"]
                        > 5
                    ):
                        print(f"Do not install {package_name}! {results!r}")
                    else:
                        print(f"{package_name} is okay to install")


class LinkerTest(CMD):
    arg_path_info = Arg(
        "path_info",
        nargs="+",
        help="end and start points for finding a back path",
    )

    async def export(self):
        linker = Linker()
        exported = linker.export(
            run_bandit.op,
            pypi_latest_package_version.op,
            pypi_package_json.op,
            pypi_package_url.op,
            pypi_package_contents.op,
            safety_check.op,
        )
        return exported

    ##TODO Multiple INPUT and Multiple OUTPUT cases
    async def run(self):
        temp = await self.export()
        dest_operation = self.path_info[0]
        init_inp = self.path_info[1]
        operations_dict = temp["operations"]
        for name, operation in operations_dict.items():
            operation["inputs"] = list(operation["inputs"].values())[0]
            operation["outputs"] = list(operation["outputs"].values())[0]
        inp = operations_dict[dest_operation]["inputs"]
        backtrack_list = [dest_operation]
        while inp != init_inp:
            for name, operation in operations_dict.items():
                if operation["outputs"] == inp:
                    backtrack_list.append(name)
                    inp = operation["inputs"]

        backtrack_list.reverse()
        return backtrack_list


class LinkerTest(CMD):
    arg_path_info = Arg(
        "path_info",
        nargs="+",
        help="end and start points for finding a back path",
    )

    async def dep_backtrack(self, *operations):
        output_dict = {}
        for operation in operations:
            temp_dict = {operation.name: operation}
            op_outputs = list(operation.outputs.values())
            for output in op_outputs:
                # TODO .update(temp-dict) if key exists, otherwise set
                output_dict[output.name] = temp_dict
        # Now we have a dict, output_dict, mapping all of the definitions to the
        # operations that create them.

        flow_dict = {}
        # Got through all the operations and look at their inputs
        for operation in operations:
            flow_dict.setdefault(operation.name, {})
            # Example operation:
            # Operation(
            #     name="pypi_package_json",
            #     # internal_name: package
            #     # definition: package = Definition(name="package", primitive="str")
            #     inputs={"package": package},
            #     # internal_name: response_json
            #     # definition: package_json = Definition(name="package_json", primitive="Dict")
            #     outputs={"response_json": package_json},
            # )
            # For each input
            for internal_name, definition in operation.inputs.items():
                # With pypi_package_json example
                # internal_name = "package"
                # definition = package
                #            = Definition(name="package", primitive="str")
                temp_l = []
                if definition.name in output_dict:
                    # Grab the dict of operations that produce this definition
                    # as an output
                    producing_operations = output_dict[definition.name]
                    # If the input could be produced by an operation in the
                    # network, then it's definition name will be in output_dict.
                    flow_dict[operation.name][internal_name] = []
                    # We look through the outputs and add any one that matches
                    # the definition and add it to the list in format of
                    # operation_name . internal_name (of output)
                    for producting_operation in producing_operations.values():
                        for (
                            internal_name_of_output,
                            output_definition,
                        ) in producting_operation.outputs.items():
                            if output_definition == definition:
                                flow_dict[operation.name][
                                    internal_name
                                ].append(
                                    producting_operation.name
                                    + "."
                                    + internal_name_of_output
                                )
                else:
                    flow_dict[operation.name][internal_name] = ["seed"]
        # print(output_dict)
        print("--------------------------")

        return flow_dict

    async def run(self):
        # Instead of path_info being start and end, make it list of loadable
        # paths to operations.
        # Meaning things that could be passed to the dffml.service.dev:Run
        # command. Look at that for more info. And copy paste the code to load
        # an operation, then once you have the code to load an operation. Append
        # the operation to a list and pass it to dep_backtrack.
        backtrack_list = await self.dep_backtrack(
            pypi_package_json.op,
            pypi_latest_package_version.op,
            pypi_package_url.op,
            pypi_package_contents.op,
            cleanup_pypi_package.op,
            run_bandit.op,
            safety_check.op,
        )

        return backtrack_list


class ShouldI(CMD):

    install = Install
    linker = LinkerTest
