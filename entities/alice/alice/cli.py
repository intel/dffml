import sys
import copy
import pathlib
import platform
import contextlib
import dataclasses
from typing import Dict, List, NewType


import dffml
import shouldi.cli
import dffml_operations_innersource.cli

from .system_context import Alice


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
    contribute = (
        dffml_operations_innersource.cli.InnerSourceCLI.run.records._set
    )
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


import dffml_feature_git.feature.definitions

# TODO GitRepoSpec resolve to correct definition on auto def
class AlicePleaseContributeRecommendedCommunityStandards:
    def has_readme(
        self,
        repo: dffml_feature_git.feature.definitions.GitRepoSpec,
    ) -> NewType("repo.directory.has.readme", bool):
        # "$REPO_DIRECTORY/README.md"
        return pathlib.Path(repo.directory, "README.md").exists()

    def has_code_of_conduct(
        self,
        repo: dffml_feature_git.feature.definitions.GitRepoSpec,
    ) -> NewType("repo.directory.has.code_of_conduct", bool):
        return pathlib.Path(repo.directory, "CODE_OF_CONDUCT.md").exists()

    def has_contributing(
        self,
        repo: dffml_feature_git.feature.definitions.GitRepoSpec,
    ) -> NewType("repo.directory.has.contributing", bool):
        return pathlib.Path(repo.directory, "CONTRIBUTING.md").exists()

    def has_license(
        self,
        repo: dffml_feature_git.feature.definitions.GitRepoSpec,
    ) -> NewType("repo.directory.has.license", bool):
        return pathlib.Path(repo.directory, "LICENSE.md").exists()

    def has_security(
        self,
        repo: dffml_feature_git.feature.definitions.GitRepoSpec,
    ) -> NewType("repo.directory.has.security", bool):
        return pathlib.Path(repo.directory, "SECURITY.md").exists()


class AlicePleaseContributeCLI(dffml.CMD):

    CONFIG = AlicePleaseContributeCLIConfig

    async def run(self):
        # TODO When running Alice from the CLI we will inspect the top level
        # system context in the furture applied overlay which is the alice
        # please contribute overlay which provides CLI applications. It should
        # auto populate the input required to the base repo dataflow.

        import os
        import textwrap
        import unittest

        content_should_be = textwrap.dedent(
            """
            - [] [README](https://github.com/intel/dffml/blob/main/README.md)
            - [] Code of conduct
            - [] [Contributing](https://github.com/intel/dffml/blob/main/CONTRIBUTING.md)
            - [] [License](https://github.com/intel/dffml/blob/main/LICENSE)
            - [] Security
            """
        ).lstrip()

        import pathlib

        @dffml.op(
            inputs={"repo": dffml_feature_git.feature.definitions.git_repository,},
            outputs={"result": NewType("repo.directory.has.readme", bool),},
        )
        def has_readme(repo):
            # "$REPO_DIRECTORY/README.md"
            return {"result": pathlib.Path(repo.directory, "README.md").exists()}

        @dffml.op(
            inputs={"repo": dffml_feature_git.feature.definitions.git_repository,},
            outputs={"result": NewType("repo.directory.has.code_of_conduct", bool),},
        )
        def has_code_of_conduct(repo):
            return {
                "result": pathlib.Path(repo.directory, "CODE_OF_CONDUCT.md").exists()
            }

        @dffml.op(
            inputs={"repo": dffml_feature_git.feature.definitions.git_repository,},
            outputs={"result": NewType("repo.directory.has.contributing", bool),},
        )
        def has_contributing(repo):
            return {"result": pathlib.Path(repo.directory, "CONTRIBUTING.md").exists()}

        @dffml.op(
            inputs={"repo": dffml_feature_git.feature.definitions.git_repository,},
            outputs={"result": NewType("repo.directory.has.license", bool),},
        )
        def has_license(repo):
            return {"result": pathlib.Path(repo.directory, "LICENSE.md").exists()}

        @dffml.op(
            inputs={"repo": dffml_feature_git.feature.definitions.git_repository,},
            outputs={"result": NewType("repo.directory.has.security", bool),},
        )
        def has_security(repo):
            return {"result": pathlib.Path(repo.directory, "SECURITY.md").exists()}

        DFFMLCLICMD = NewType("dffml.util.cli.CMD", object)

        @dffml.op(
            inputs={"cmd": DFFMLCLICMD,},
            outputs={"repo": dffml_feature_git.feature.definitions.git_repository,},
            expand=["repo"],
        )
        def cli_is_meant_on_this_repo(cmd):
            return {
                "repo": [
                    dffml_feature_git.feature.definitions.GitRepoSpec(
                        directory=os.getcwd(), URL=None,
                    ),
                ]
                if not cmd.repos
                else []
            }

        @dffml.op(
            inputs={"cmd": DFFMLCLICMD,},
            outputs={"repo": dffml_feature_git.feature.definitions.git_repository,},
            expand=["repo"],
        )
        def cli_has_repos(cmd):
            return {
                "repo": [
                    dffml_feature_git.feature.definitions.GitRepoSpec(
                        directory=repo, URL=repo,
                    )
                    for repo in cmd.repos
                ]
            }

        async for ctx, results in dffml.run(
            dffml.DataFlow(*dffml.opimp_in(locals())),
            [dffml.Input(value=self, definition=DFFMLCLICMD,),],
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

        # TODO Implement creation of issues once we have body text generation
        # working.


class AlicePleaseCLI(dffml.CMD):

    contribute = AlicePleaseContributeCLI


class AliceCLI(dffml.CMD):

    shouldi = ShouldiCLI
    threats = AliceThreatsMd
    please = AlicePleaseCLI
    # TODO 2022-05-26 13:15 PM PDT: Maybe this should be a dataflow rather than
    # a system context? Or support both more likely.
    # version = DataFlow(op(stage=Stage.OUTPUT)(get_alice_version))
    # TODO Set parent as Input when runing and after overlay!!!
    # parent=None,
    # inputs=[]
    # architecture=OpenArchitecture(dataflow=DataFlow(op(stage=Stage.OUTPUT)(get_alice_version))),
    # orchestrator=MemoryOrchestrator(),
    # If we want results to be AliceVersion. Then we need to run the
    # operation which produces AliceVersion as an output operation.
    #
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO 2022-05-26 12:53 PM PDT  TODO TODO TODO
    # TODO TODO TODO        SEE BELOW         TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    #
    # THE TODO: We want grab SemanticVersion. Look for types who's liniage
    # is derived from that. If there is no operation which outputs a derived
    # or direct type. Raise invalid.
    #
    # We will overlay output operations and check validity
    #
    # For a system context to be used as a CLI command we will overlay with
    # an output operation which returns a single result within
    # dffml.util.cli.cmd. This flow should produce a result of the CLI
    # result data type. This flow should have an operation in it which
    # produces cli_result via taking a single peice of data derived from
    # SemanticVersion.
    #
    # We can check if we can use the System Context as a CLI command by
    # checking if it's valid when we overlay a system context which has an
    # the following input in it: `cli_result`. If we are we get an invalid
    # context, we know that we cannot use this as a CLI command, since it
    # doesn't produce a CLI result.
    #
    # Maybe we know that all CLI commands must accept an input int
    # architecture=OpenArchitecture(dataflow=DataFlow(op(stage=Stage.OUTPUT)(get_alice_version))),
    # version = Alice.only("version")
