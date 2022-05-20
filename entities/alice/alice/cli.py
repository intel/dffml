import sys
import copy
import pathlib
import platform
import contextlib
import dataclasses
from typing import Dict

import dffml
import shouldi.cli
import dffml_operations_innersource.cli


class ShouldiCLI(dffml.CMD):

    # TODO Overlay dataflow so that upstream shouldi install is used as part of
    # our python package evauation
    # TODO Take PURL or SW Heritage ID as an input definition
    use = shouldi.cli.ShouldI.install
    reuse = shouldi.use.Use
    contribute = dffml_operations_innersource.cli.InnerSourceCLI.run.records._set
    # diagram = ShouldiDiagram


class AliceProduceCLI(dffml.CMD):

    sbom = shouldi.project.cli.ProjectCMD.create


class AliceCLI(dffml.CMD):

    produce = AliceProduceCLI


class AliceCLI(dffml.CMD):

    shouldi = ShouldiCLI
