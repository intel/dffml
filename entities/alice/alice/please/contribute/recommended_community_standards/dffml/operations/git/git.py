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
import dffml_feature_git.feature.definitions


from ....recommended_community_standards import AliceGitRepo, AlicePleaseContributeRecommendedCommunityStandards


# An overlay which could be installed if you have dffml-feature-git
# (aka dffml-operations-git) installed.
class AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:
    GuessedGitURL = NewType("guessed.git.url", bool)
    DefaultBranchName = NewType("default.branch.name", str)

    # The operations we use defined elsewhere
    check_if_valid_git_repository_URL = (
        dffml_feature_git.feature.operations.check_if_valid_git_repository_URL
    )
    clone_git_repo = dffml_feature_git.feature.operations.clone_git_repo
    git_repo_default_branch = (
        dffml_feature_git.feature.operations.git_repo_default_branch
    )

    async def create_branch_if_none_exists(
        self, repo: AliceGitRepo, name: Optional["DefaultBranchName"] = "main",
    ) -> dffml_feature_git.feature.definitions.GitBranchType:
        """
        If there are no branches, the git_repo_default_branch operation will
        return None, aka there si no default branch. Therefore, in this
        operation, we check if there are any branches at all, and if there are
        not we create a new branch. We could optionally facilitate interaction
        of multiple similar operations which wish to create a default branch if
        none exist by creating a new defintion which is locked which could be
        used to synchronise communication aka request for lock from some service
        which has no native locking (transmistion of NFT via DIDs over abitrary
        channels for example).
        """
        branches = (
            await dffml_feature_git.feature.operations.check_output(
                "git", "branch", "-r", cwd=repo.directory
            )
        ).split("\n")
        # If there's branches then bail out
        if list(filter(bool, branches)):
            return
        await dffml.run_command(
            ["git", "branch", "-M", name], cwd=repo.directory, logger=self.logger,
        )
        await dffml.run_command(
            ["git", "commit", "-m", "Created branch", "--allow-empty"],
            logger=self.logger,
        )
        return name

    def guess_repo_string_is_url(
        self,
        repo_string: AlicePleaseContributeRecommendedCommunityStandards.RepoString,
    ) -> GuessedGitURL:
        if "://" not in repo_string:
            return
        return repo_string

    def guessed_repo_string_means_no_git_branch_given(
        repo_url: GuessedGitURL,
    ) -> dffml_feature_git.feature.definitions.NoGitBranchGivenType:
        # TODO Support _ prefixed unused variables (repo_url used to trigger,
        # always true on trigger).
        return True

    def guessed_repo_string_is_operations_git_url(
        repo_url: GuessedGitURL,
    ) -> dffml_feature_git.feature.definitions.URLType:
        return repo_url
