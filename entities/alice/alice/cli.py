import os
import sys
import copy
import pathlib
import inspect
import argparse
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


from .system_context import Alice, alice_version

# from .threats_md import THREATS_MD_DATAFLOW
THREATS_MD_DATAFLOW = dffml.DataFlow()
from .please.contribute.recommended_community_standards.recommended_community_standards import (
    AlicePleaseContributeRecommendedCommunityStandards,
)
from .please.contribute.recommended_community_standards.cli import DFFMLCLICMD


# TODO Make this use the overlay stuff on runtime instead of on module load.
ALICE_COLLECTOR_DATAFLOW = dffml_operations_innersource.cli.COLLECTOR_DATAFLOW


# NOTE When CLI and operations are merged: All this is the same stuff that will
# happen to Operation config_cls structures. We need a more ergonomic API to
# obsucre the complexity dataclasses introduces when modifying fields/defaults
# within subclasses.
for (new_class_name, dffml_cli_class), field_modifications in {
    ("AliceThreatsMd", dffml.cli.dataflow.RunSingle): {
        "dataflow": {"default_factory": lambda: THREATS_MD_DATAFLOW},
        "no_echo": {"default": True},
    },
    (
        "AliceShouldIContribute",
        dffml_operations_innersource.cli.InnerSourceCLI.run.records._set,
    ): {
        "dataflow": {"default_factory": lambda: ALICE_COLLECTOR_DATAFLOW},
    },
}.items():
    # Create a derived class
    new_class = dffml_cli_class.subclass(new_class_name, field_modifications)
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
    contribute = AliceShouldIContribute
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


# TODO(alice) Replace with definition as system context
# AlicePleaseContributeRecommendedCommunityStandards.sysctx = object()
# AlicePleaseContributeRecommendedCommunityStandards.sysctx.upstream = AlicePleaseContributeCLIDataFlow = dffml.DataFlow(
AlicePleaseContributeCLIDataFlow = dffml.DataFlow(
    *itertools.chain(
        *[
            dffml.object_to_operations(cls)
            for cls in [
                AlicePleaseContributeRecommendedCommunityStandards,
                # *AlicePleaseContributeRecommendedCommunityStandards.overlays(),
                *dffml.Overlay.load(
                    entrypoint="dffml.overlays.alice.please.contribute.recommended_community_standards"
                ),
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
    create = dffml.CMD.from_entrypoint("AlicePleaseCreateCLI", "alice.please.create")


class AliceVersionCLI(dffml.CMD):
    async def run(self):
        print(alice_version())


class AliceCLI(dffml.CMD):
    r"""
                            .,*&&888@@#&:,
                          .:&::,...,:&#@@@#:.
                         .o,.       ..:8@@#@@+
                        .8o+,+o*+*+,+:&#@@#8@@.
                        &8&###@#&..*:8#@@#@#@@&+.
                       ,@:#@##@@8,:&#@@@###@88@@.
                      ,#@8&#@@@#o:#@@@@#8#@#8+&#.
                     +8####@@@@###@@@888#@@@#oo#.
                   .*8@###@@@@@@@@@#o*#@@#@@#8o@,
                  +###@#o8&#@@##8::##@@@&&#@8#&+
                  o@8&#&##::.,o&+88#&8##8*@@#@#,
                 .##888&&oo#&o8###8&o##8##&####8,
                .&#@8&:+o+&@@@#8#&8:8@@@@@#8@@@oo+
               ,&&#@##oo+*:@###&#88,@@@@#@o&##&8#@o,.
              ,#&###@@8:*,#o&@@@@##:&#@###*.&o++o#@@#&+
              o8&8o8@#8+,,#.88#@#&@&&#@##++*&#o&&&#@@@@.
              *88:,#8&#,o+:+@&8#:8@8&8#@@&o++,*++*+:#@@*.
              .+#:o###@8o&8*@o&o8@o888@@@o+:o*&&,@#:&@@@,
                *+&@8&#@o#8+8*#+8#+88@@@@@@&@###8##@8:*,
                  +o.@##@@@&88@*8@:8@@@@@@:.. ,8@:++.
                    +&++8@@@@##@@@@@@@@@@@+    88
                    &.   *@8@:+##o&888#@@@,   .#+
                    &.   ,@+o,.::+*+*:&#&,    ,@.
                    &.   .@8*,. ,*+++.+*     :8+
                    :+   .#@::. .8:.:**    .8@@o,
                    .o.   #@+   :@,.&*   .:@@@@@@8**.
                     +&.  :@o,+.*o,*,  .*@@@@@@@@@@#o
                   .*:&o.  8@o:,*:,  .o@@#8&&@@@@#@@@*
                 ,*:+:::o.*&8+,++  ,&@@#:  * :@@88@@@#:.
               ,::**:o:.,&*+*8:  *8@@##o   *,.8@@#8#@#@#+
              *:+*&o8:. ,o,o:8@+o@@88:*@+  +: +#@#####8##&.
            ,:&::88&,   .&:#o#@@@#,+&&*#&. .:,.&#@#88#####&,
           +::o+&8:.    :##88@@@@:.:8o+&8&. .. +8###&8&##&88*
         .:*+*.8#:    ,o*.+&@@#@8,,o8*+8##+    .+#8##8&&#8888:.
        ,:o., &#8.  .:8*.  .o, &#,*:8:+,&*:,    .8@@#o&&##8:&#8.
      .*o.*,+o8#*  +8&,  .::. .88.+:8o: ,+:,    ,o#@#8&o8##&#8+
     +o, .+,,o#8+,8@o**.,o*,  :8o +*8#*  +&,    ,*o@@#@&8&oo8&:,
    oo*+,,,*8@#..&@8:**:oo+. +8#* *+#@:...oo+  .**:8@@@ooo&:&o##+
    ::+..,++#@,.:##o&o**,....oo#++#8#@:.,:8&:.....*&@@#:oo*&oo&#@*
     .+**:*8@o,+##&o:+,,,+,,o*8#,,8@#@:,,+*o*++,,,,+&#@8*8o88&::*.
         ..8@++#@#88:,,,.,,,:+#&,,#@@#:,,.,&o*,.+++*:#@8+:*+.
            +:&8#@@##8&+,,,***@&,.8@@@*,,,.:o8&o&*o&o&o.
                 ...,*:*o&&o*8@@&o8@@@8+,,+:&&:+,...
                        o@#@@@@#@@@@@@@,.....
                        ,@##@@88#@@@@@8
                         8+.,8+..,*o#@+
                         *o  *+     #8
                          8, ,&    +@*
                          +&  &,  .@#.
                           o* ,o  o@&
                           .8. 8.,o#8
                            8. 8.,.&@:*:&@.
                           :@o:#,,o8&:o&@@.
                          .@@@@@@@@@@@#8.
                           ,*:&#@#&o*,

                                /\
                               /  \
                              Intent
                             /      \
                            /        \
                           /          \
                          /            \
                         /              \
                        /  Alice is Here \
                       /                  \
                      /                    \
                     /______________________\

             Dynamic Analysis          Static Analysis

    Alice's source code: https://github.com/intel/dffml/tree/alice/entities/alice
    How we built Alice: https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice
    How to extend Alice: https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst
    Comment to get involved: https://github.com/intel/dffml/discussions/1406
    """
    CLI_FORMATTER_CLASS = argparse.RawDescriptionHelpFormatter

    shouldi = ShouldiCLI
    threats = AliceThreatsMd
    please = AlicePleaseCLI
    version = AliceVersionCLI
