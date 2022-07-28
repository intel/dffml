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

from .recommended_community_standards import (
    AlicePleaseContributeRecommendedCommunityStandards,
)


DFFMLCLICMD = NewType("dffml.util.cli.CMD", object)
AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI = NewType(
    "AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI", bool
)

# TODO A way to deactivate installed overlays so they are not merged or applied.
class OverlayCLI:
    CLIRunOnRepo = NewType("CLIRunOnRepo", str)

    @staticmethod
    def cli_is_asking_for_recommended_community_standards(
        cmd: DFFMLCLICMD,
    ) -> AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI:
        """

        .. code-block:: console
            :test:

            $ alice please contribute recommended community standards


        """
        if not "" in cmd.extra_config:
            return
        args = cmd.extra_config[""]["plugin"]
        if not isinstance(args, list):
            return
        return "recommended community standards" in " ".join(args)

    async def cli_is_meant_on_this_repo(
        self,
        cmd: DFFMLCLICMD,
        wanted: AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI,
    ) -> AsyncIterator["CLIRunOnRepo"]:
        if not wanted or cmd.repos:
            return
        yield os.getcwd()

    @staticmethod
    async def cli_has_repos(
        cmd: DFFMLCLICMD,
        wanted: AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI,
    ) -> AsyncIterator["CLIRunOnRepo"]:
        if not wanted:
            return
        # TODO directory should really be None
        for repo in cmd.repos:
            yield repo

    async def cli_run_on_repo(
        self, repo: "CLIRunOnRepo"
    ) -> AlicePleaseContributeRecommendedCommunityStandards.RepoString:
        # TODO Similar to Expand being an alias of Union
        #
        # async def cli_run_on_repo(self, repo: 'CLIRunOnRepo') -> SystemContext[StringInputSetContext[AliceGitRepo]]:
        #     return repo
        #
        # Or ideally at class scope
        #
        # 'CLIRunOnRepo' -> SystemContext[StringInputSetContext[AliceGitRepo]]
        """
        async with dffml.run_dataflow.imp(
            dataflow=self.octx.config.dataflow,
        ) as custom_run_dataflow:
            async with custom_run_dataflow(
                self.ctx, self.octx
            ) as custom_run_dataflow_ctx:
                # This is the type cast
                custom_run_dataflow.op = custom_run_dataflow.op._replace(
                    inputs={
                        "repo": AlicePleaseContributeRecommendedCommunityStandards.RepoString
                    },
                    outputs={},
                )
                # Set the dataflow to be the same flow
                await dffml.run_dataflow.run_custom(
                    custom_run_dataflow_ctx, {"repo": repo},
                )
        """
        # TODO Clean this up once SystemContext refactor complete
        # This is used to ensure we don't add any inputs that would retrigger
        # any operations within this overlay when calling the subflow.
        overlay_cli_dataflow = dffml.DataFlow(
            *itertools.chain(
                *[
                    dffml.object_to_operations(cls)
                    for cls in [
                        OverlayCLI,
                        *dffml.Overlay.load(
                            entrypoint="dffml.overlays.alice.please.contribute.recommended_community_standards.overlay.cli"
                        ),
                    ]
                ]
            )
        )
        # TODO copy.deepcopy(self.octx.config.dataflow)?
        async with dffml.run_dataflow.imp(
            dataflow=copy.deepcopy(self.octx.config.dataflow),
        ) as custom_run_dataflow:
            # Copy all inputs from parent context into child. We eventually
            # should have InputNetworks which support acting as generic Copy on
            # Write over an underlying InputNetwork.
            async with custom_run_dataflow(
                self.ctx, self.octx
            ) as custom_run_dataflow_ctx:
                async with self.octx.ictx.definitions(self.ctx) as definitions:
                    custom_run_dataflow.config.dataflow.seed = (
                        custom_run_dataflow.config.dataflow.seed
                        + [
                            item
                            async for item in definitions.inputs()
                            if (
                                item.definition
                                in custom_run_dataflow.config.dataflow.definitions.values()
                                and item.definition
                                not in overlay_cli_dataflow.definitions.values()
                            )
                        ]
                    )
                input_key = list(self.parent.op.inputs.keys())[0]
                key, definition = list(self.parent.op.outputs.items())[0]
                # This is the type cast
                custom_run_dataflow.op = custom_run_dataflow.op._replace(
                    # TODO Debug why the commented out version doesn't work
                    # Likely due to re-auto-definition
                    inputs={input_key: definition},
                    outputs={},
                )
                await dffml.run_dataflow.run_custom(
                    custom_run_dataflow_ctx,
                    {
                        input_key: dffml.Input(
                            value=repo,
                            definition=definition,
                            parents=None,
                            origin=(self.parent.op.instance_name, key),
                        )
                    },
                )
