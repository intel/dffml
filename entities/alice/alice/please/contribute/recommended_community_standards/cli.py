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

from .recommended_community_standards import AlicePleaseContributeRecommendedCommunityStandards


DFFMLCLICMD = NewType("dffml.util.cli.CMD", object)
AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI = NewType(
    "AlicePleaseContributeRecommendedCommunityStandardsExecutedFromCLI", bool
)

# TODO A way to deactivate installed overlays so they are not merged or applied.
class AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:
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

    async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
        # TODO Similar to Expand being an alias of Union
        #
        # async def cli_run_on_repo(self, repo: 'CLIRunOnRepo') -> SystemContext[StringInputSetContext[AliceGitRepo]]:
        #     return repo
        #
        # Or ideally at class scope
        #
        # 'CLIRunOnRepo' -> SystemContext[StringInputSetContext[AliceGitRepo]]
        async with self.parent.__class__(self.parent.config) as custom_run_dataflow:
            async with custom_run_dataflow(
                self.ctx, self.octx
            ) as custom_run_dataflow_ctx:
                # This is the type cast
                custom_run_dataflow.op = self.parent.op._replace(
                    inputs={
                        "repo": AlicePleaseContributeRecommendedCommunityStandards.RepoString
                    }
                )
                # Set the dataflow to be the same flow
                # TODO Reuse ictx? Is that applicable?
                custom_run_dataflow.config.dataflow = self.octx.config.dataflow
                await dffml.run_dataflow.run_custom(
                    custom_run_dataflow_ctx, {"repo": repo},
                )
