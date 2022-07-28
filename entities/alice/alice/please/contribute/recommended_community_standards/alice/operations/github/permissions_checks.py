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
from dffml_feature_git.feature.definitions import git_remote

from ....recommended_community_standards import (
    AliceGitRepo,
    AlicePleaseContributeRecommendedCommunityStandards,
)
from .pull_request import (
    AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest,
)


async def github_owns_remote(
    self, directory: str, check_remote: str, *, logger=None,
) -> bool:
    remotes = {}
    async for event, result in dffml.run_command_events(
        ["git", "remote", "-v"],
        cwd=directory,
        logger=logger,
        events=[dffml.Subprocess.STDOUT_READLINE],
    ):
        if event is dffml.Subprocess.STDOUT_READLINE:
            remote, url_and_usages = result.decode().strip().split("\t", maxsplit=2)
            if remote != check_remote:
                continue
            url = url_and_usages.split()[0]
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
                logger=logger,
                events=[dffml.Subprocess.STDOUT],
            ):
                result = result.strip().decode()
                if event is dffml.Subprocess.STDOUT and result in ("ADMIN", "MAINTAIN"):
                    return True
    return False


class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubWritableRemotesFromPermissions:
    async def github_owns_remote(
        self, repo: AliceGitRepo, remote: git_remote,
    ) -> AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest.WriteableGitRemoteOrigin:
        if repo.URL is None or not await github_owns_remote(
            self, repo.directory, remote, logger=self.logger
        ):
            return
        return remote
