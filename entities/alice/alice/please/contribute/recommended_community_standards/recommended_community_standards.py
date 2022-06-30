import pathlib
from typing import NamedTuple, Optional, NewType


class AliceGitRepo(NamedTuple):
    directory: str
    URL: str


# @base_entry_point("dffml.overlays.alice.please.contribute.recommended_community_standards")
# TODO GitRepoSpec resolve to correct definition on auto def
class AlicePleaseContributeRecommendedCommunityStandards:
    # TODO SystemContext __new__ auto populate config to have upstream set to
    # dataflow generated from methods in this class with memory orchestarator.
    ReadmePath = NewType("ReadmePath", object)
    RepoString = NewType("repo.string", str)
    ReadmeContents = NewType("repo.directory.readme.contents", str)
    HasReadme = NewType("repo.directory.readme.exists", bool)

    # TODO Generate output definition when wrapped with op decorator, example:
    #   HasReadme = NewType("AlicePleaseContributeRecommendedCommunityStandards.has.readme", bool)

    # TODO
    # ) -> bool:
    # ...
    #     has_readme: 'has_readme',

    async def guess_repo_string_is_directory(
        repo_string: "RepoString",
    ) -> AliceGitRepo:
        # TODO(security) How bad is this?
        if not pathlib.Path(repo_string).is_dir():
            return
        return AliceGitRepo(directory=repo_string, URL=None)

    # TODO Run this system context where readme contexts is given on CLI or
    # overriden via disabling of static overlay and application of overlay to
    # generate contents dynamiclly.
    def create_readme_file_if_not_exists(
        self,
        repo: AliceGitRepo,
        readme_contents: Optional["ReadmeContents"] = "# My Awesome Project's README",
    ) -> "ReadmePath":
        # Do not create readme if it already exists
        path = pathlib.Path(repo.directory, "README.md")
        if path.exists():
            return path
        path.write_text(readme_contents)
        return path
