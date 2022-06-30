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

from ....recommended_community_standards import AliceGitRepo, AlicePleaseContributeRecommendedCommunityStandards
from .pull_request import AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest


class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubWritableRemotesFromPermissions:
    async def already_owns_repo(
        self, repo: AliceGitRepo,
    ) -> AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest.WriteableGitRemoteOrigin:
        if repo.URL is None:
            return
        origins = {}
        async for event, result in dffml.run_command_events(
            ["git", "remote", "-v"],
            cwd=repo.directory,
            logger=self.logger,
            events=[dffml.Subprocess.STDOUT_READLINE],
        ):
            if event is dffml.Subprocess.STDOUT_READLINE:
                origin, url_and_usages = result.decode().strip().split("\t", maxsplit=2)
                origins[origin] = url_and_usages.split()[0]
        for origin, url in origins.items():
            async for event, result in dffml.run_command_events(
                [
                    "gh",
                    "repo",
                    "view",
                    url,
                    "--json",
                    "viewerPermission",
                    "-q",
                    ".viewerPermission",
                ],
                logger=self.logger,
                events=[dffml.Subprocess.STDOUT],
            ):
                result = result.strip().decode()
                if event is dffml.Subprocess.STDOUT and result in (
                    "ADMIN",
                    "MAINTAIN",
                ):
                    return origin
