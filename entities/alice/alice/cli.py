import sys
import copy
import pathlib
import platform
import contextlib
import dataclasses
from typing import Dict, NewType


import dffml
import shouldi.cli
import dffml_operations_innersource.cli

from .system_context import Alice


class ShouldiCLI(dffml.CMD):

    # TODO Overlay dataflow so that upstream shouldi install is used as part of
    # our python package evauation
    # TODO Take PURL or SW Heritage ID as an input definition
    use = shouldi.cli.ShouldI.install
    reuse = shouldi.use.Use
    contribute = (
        dffml_operations_innersource.cli.InnerSourceCLI.run.records._set
    )
    # diagram = ShouldiDiagram


class AliceProduceCLI(dffml.CMD):

    sbom = shouldi.project.cli.ProjectCMD.create


class AliceCLI(dffml.CMD):

    produce = AliceProduceCLI


class AliceCLI(dffml.CMD):

    shouldi = ShouldiCLI
    # TODO 2022-05-26 13:15 PM PDT: Maybe this should be a dataflow rather than
    # a system context? Or support both more likely.
    # version = DataFlow(op(stage=Stage.OUTPUT)(get_alice_version))
    # TODO Set parent as Input when runing and after overlay!!!
    # parent=None,
    # inputs=[]
    # architecture=OpenArchitecture(dataflow=DataFlow(op(stage=Stage.OUTPUT)(get_alice_version))),
    # orchestrator=MemoryOrchestrator(),
    # If we want results to be AliceVersion. Then we need to run the
    # operation which produces AliceVersion as an output operation.
    #
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO 2022-05-26 12:53 PM PDT  TODO TODO TODO
    # TODO TODO TODO        SEE BELOW         TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    #
    # THE TODO: We want grab SemanticVersion. Look for types who's liniage
    # is derived from that. If there is no operation which outputs a derived
    # or direct type. Raise invalid.
    #
    # We will overlay output operations and check validity
    #
    # For a system context to be used as a CLI command we will overlay with
    # an output operation which returns a single result within
    # dffml.util.cli.cmd. This flow should produce a result of the CLI
    # result data type. This flow should have an operation in it which
    # produces cli_result via taking a single peice of data derived from
    # SemanticVersion.
    #
    # We can check if we can use the System Context as a CLI command by
    # checking if it's valid when we overlay a system context which has an
    # the following input in it: `cli_result`. If we are we get an invalid
    # context, we know that we cannot use this as a CLI command, since it
    # doesn't produce a CLI result.
    #
    # Maybe we know that all CLI commands must accept an input int
    # architecture=OpenArchitecture(dataflow=DataFlow(op(stage=Stage.OUTPUT)(get_alice_version))),
    version = Alice.only("version")
