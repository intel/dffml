import os
import sys
import copy
import pathlib
import inspect
import textwrap
import unittest
import platform
import itertools
import contextlib
import dataclasses
from typing import Dict, List, Optional, AsyncIterator, NamedTuple, NewType


import dffml
import shouldi.cli
import dffml_operations_innersource.cli

from .system_context import Alice
# from .threats_md import THREATS_MD_DATAFLOW
THREATS_MD_DATAFLOW = dffml.DataFlow()
from .please.contribute.recommended_community_standards.recommended_community_standards import AlicePleaseContributeRecommendedCommunityStandards
from .please.contribute.recommended_community_standards.cli import DFFMLCLICMD


# NOTE When CLI and operations are merged: All this is the same stuff that will
# happen to Operation config_cls structures. We need a more ergonomic API to
# obsucre the complexity dataclasses introduces when modifying fields/defaults
# within subclasses.
for dffml_cli_class_name, field_modifications in {
    "RunSingle": {
        "dataflow": {"default_factory": lambda: THREATS_MD_DATAFLOW},
        "no_echo": {"default": True},
    },
}.items():
    # Create the class and config names by prepending InnerSource
    new_class_name = "AliceThreatsMd"
    # Create a derived class
    new_class = getattr(dffml.cli.dataflow, dffml_cli_class_name).subclass(
        new_class_name, field_modifications,
    )
    # Add our new class to the global namespace
    setattr(
        sys.modules[__name__], new_class.CONFIG.__qualname__, new_class.CONFIG,
    )
    setattr(
        sys.modules[__name__], new_class.__qualname__, new_class,
    )


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


@dffml.config
class AlicePleaseContributeCLIConfig:
    repos: List[str] = dffml.field(
        "Repos to contribute to", default_factory=lambda: [],
    )


def object_to_operations(obj, module=None):
    """
    Takes an object and creates a list of operations for that object, after
    wrapping any likely targets (functions, methods) with op.
    """
    if module is not None:
        if not inspect.ismodule(module):
            raise TypeError(f"{module} is not a module")
        python_path = f"{module.__name__}"
    elif inspect.ismodule(obj):
        return object_to_operations(obj, module=obj)
    else:
        python_path = f"{obj.__module__}.{obj.__qualname__}"
    return [
        dffml.op(name=f"{python_path}:{name}")(method)
        if not hasattr(method, "imp")
        else method.imp
        for name, method in inspect.getmembers(
            obj,
            predicate=lambda i: inspect.ismethod(i)
            or inspect.isfunction(i)
            and not hasattr(i, "__supertype__"),
        )
    ]

# TODO(alice) Replace with definition as system context
# AlicePleaseContributeRecommendedCommunityStandards.sysctx = object()
# AlicePleaseContributeRecommendedCommunityStandards.sysctx.upstream = AlicePleaseContributeCLIDataFlow = dffml.DataFlow(
AlicePleaseContributeCLIDataFlow = dffml.DataFlow(
    *itertools.chain(
        *[
            object_to_operations(cls)
            for cls in [
                AlicePleaseContributeRecommendedCommunityStandards,
                # *AlicePleaseContributeRecommendedCommunityStandards.overlays(),
                *dffml.Overlay.load(entrypoint="dffml.overlays.alice.please.contribute.recommended_community_standards")
            ]
        ]
    )
)


class AlicePleaseContributeCLI(dffml.CMD):

    CONFIG = AlicePleaseContributeCLIConfig
    DATAFLOW = AlicePleaseContributeCLIDataFlow

    async def run(self):
        # TODO When running Alice from the CLI we will inspect the top level
        # system context in the furture applied overlay which is the alice
        # please contribute overlay which provides CLI applications. It should
        # auto populate the input required to the base repo dataflow.
        content_should_be = textwrap.dedent(
            """
            - [] [README](https://github.com/intel/dffml/blob/main/README.md)
            - [] Code of conduct
            - [] [Contributing](https://github.com/intel/dffml/blob/main/CONTRIBUTING.md)
            - [] [License](https://github.com/intel/dffml/blob/main/LICENSE)
            - [] Security
            """
        ).lstrip()

        # TODO Use overlays instead of combining all classes into one
        # TODO(alice) ctx is the system context, so it will have an orchestartor
        # property on it with the orchestrator which is yielding these results.
        async for ctx, results in dffml.run(
            self.DATAFLOW, [dffml.Input(value=self, definition=DFFMLCLICMD,),],
        ):
            print((await ctx.handle()).as_string(), results)

        return

        async for ctx, results in dffml.run(
            AlicePleaseContributeRecommendedCommunityStandards,
            # dffml.DataFlow(*dffml.opimp_in(locals())),
            [dffml.Input(value=self, definition=DFFMLCLICMD,),],
            # TODO Merge all overlays into one and then run
            overlay=AlicePleaseContributeRecommendedCommunityStandardsCLIOverlay,
        ):
            (await ctx.handle()).as_string()

        content_was = textwrap.dedent(
            """
            - [] [README](https://github.com/intel/dffml/blob/main/README.md)
            - [] Code of conduct
            - [] [Contributing](https://github.com/intel/dffml/blob/main/CONTRIBUTING.md)
            - [] [License](https://github.com/intel/dffml/blob/main/LICENSE)
            - [] Security
            """
        ).lstrip()

        unittest.TestCase().assertEqual(content_should_be, content_was)


class AlicePleaseCLI(dffml.CMD):

    contribute = AlicePleaseContributeCLI


class AliceCLI(dffml.CMD):

    shouldi = ShouldiCLI
    threats = AliceThreatsMd
    please = AlicePleaseCLI
