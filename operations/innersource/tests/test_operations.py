import sys
import copy
import pathlib
import itertools

from dffml.df.types import Input, DataFlow
from dffml.df.base import opimp_in
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operations_innersource.operations import *
from dffml_feature_git.feature.operations import (
    check_if_valid_git_repository_URL,
    clone_git_repo,
    cleanup_git_repo,
)

OPIMPS = opimp_in(sys.modules[__name__])

DFFML_ROOT_DIR = pathlib.Path(__file__).parents[3]

DATAFLOW = DataFlow.auto(
    *OPIMPS,
)


class TestOperations(AsyncTestCase):
    async def test_run(self):
        dataflow = copy.deepcopy(DATAFLOW)
        # Tell the dataflow to accept repo inputs with an origin of seed (the
        # default origin for when inputs are added on dataflow start). Where the
        # input definition name is the name of the repo definition.
        dataflow.flow[github_workflow_present.op.name].inputs["repo"] += [
            {"seed": [github_workflow_present.op.inputs["repo"].name]},
        ]
        # Update flow mappings
        dataflow.update()
        await self.assertRunDataFlow(dataflow, {
            "dffml": (
                [
                    Input(
                        value=github_workflow_present.op.inputs["repo"].spec(
                            directory=DFFML_ROOT_DIR,
                        ),
                        definition=github_workflow_present.op.inputs["repo"],
                    ),
                    Input(
                        value=list(itertools.chain(*[
                            [
                                definition.name
                                for definition in opimp.op.outputs.values()
                            ]
                            for opimp in OPIMPS
                            # The operations we don't care to compare outputs
                            if opimp.op.name not in [
                                GetSingle.op.name,
                                clone_git_repo.op.name,
                                check_if_valid_git_repository_URL.op.name,
                            ]
                        ])),
                        definition=GetSingle.op.inputs["spec"],
                    ),
                ],
                {
                    github_workflow_present.op.outputs["result"].name: True
                },
            )
        })

    async def test_on_repos(self):
        dataflow = copy.deepcopy(DATAFLOW)
        await self.assertRunDataFlow(dataflow, {
            "dffml": (
                [
                    Input(
                        value="https://github.com/pdxjohnny/httptest",
                        definition=clone_git_repo.op.inputs["URL"],
                    ),
                    Input(
                        value=list(itertools.chain(*[
                            [
                                definition.name
                                for definition in opimp.op.outputs.values()
                            ]
                            for opimp in OPIMPS
                            # The operations we don't care to compare outputs
                            if opimp.op.name not in [
                                GetSingle.op.name,
                                clone_git_repo.op.name,
                                check_if_valid_git_repository_URL.op.name,
                            ]
                        ])),
                        definition=GetSingle.op.inputs["spec"],
                    ),
                ],
                {
                    github_workflow_present.op.outputs["result"].name: True,
                },
            )
        })
