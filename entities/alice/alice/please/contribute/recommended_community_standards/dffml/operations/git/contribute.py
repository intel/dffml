from typing import NewType


import dffml
import dffml_feature_git.feature.definitions

from ....recommended_community_standards import AliceGitRepo, AlicePleaseContributeRecommendedCommunityStandards


# This overlay has a suggested companion overlay of
# AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit due to
# it providing inputs this overlay needs, could suggest to use overlays together
# based of this info.
class AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:
    ReadmeCommitMessage = NewType("repo.readme.git.commit.message", str)
    ReadmeBranch = NewType("repo.readme.git.branch", str)
    BaseBranch = NewType("repo.git.base.branch", str)

    @staticmethod
    def determin_base_branch(
        default_branch: dffml_feature_git.feature.definitions.GitBranchType,
    ) -> "BaseBranch":
        # TODO .tools/process.yml which defines branches to contibute to under
        # different circumstances. Model with Linux kernel for complex case,
        # take KVM.
        # Later do NLP on contributing docs to determine
        return default_branch

    async def contribute_readme_md(
        self,
        repo: AliceGitRepo,
        base: "BaseBranch",
        commit_message: "ReadmeCommitMessage",
    ) -> "ReadmeBranch":
        branch_name: str = "alice-contribute-recommended-community-standards-readme"
        # Attempt multiple commands
        async for event, result in dffml.run_command_events(
            ["git", "checkout", base, "-b", branch_name,],
            cwd=repo.directory,
            logger=self.logger,
            raise_on_failure=False,
            events=[dffml.Subprocess.STDERR, dffml.Subprocess.COMPLETED,],
        ):
            if event is dffml.Subprocess.STDERR:
                if b"is not a commit and a branch" in result:
                    # Retry without explict branch when repo has no commits
                    await dffml.run_command(
                        ["git", "checkout", "-b", branch_name,],
                        cwd=repo.directory,
                        logger=self.logger,
                    )
            elif event is dffml.Subprocess.COMPLETED:
                if result != 0:
                    raise RuntimeError("Failed to create branch for contribution")
        await dffml.run_command(
            ["git", "add", "README.md"], cwd=repo.directory, logger=self.logger,
        )
        await dffml.run_command(
            ["git", "commit", "-sm", commit_message],
            cwd=repo.directory,
            logger=self.logger,
        )
        return branch_name
