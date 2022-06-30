import dffml_feature_git.feature.definitions

from .git import AliceGitRepo


class AlicePleaseContributeRecommendedCommunityStandardsOverlayAliceOperationsGit:
    def git_repo_to_alice_git_repo(
        repo: dffml_feature_git.feature.definitions.git_repository,
    ) -> AliceGitRepo:
        return repo
