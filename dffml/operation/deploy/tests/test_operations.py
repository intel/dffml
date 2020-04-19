import os
import sys
import tempfile
from unittest import mock

from dffml.df.types import Input, DataFlow
from dffml.df.base import opimp_in
from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase

from dffml.base import BaseDataFlowFacilitatorObjectContext


from dffml.operation.output import GetSingle
from deploy.operations import *
from dffml_feature_git.feature.operations import clone_git_repo
from dffml_feature_git.util.proc import check_output


OPIMPS = opimp_in(sys.modules[__name__])
DOCKERFILE_CONTENT =(
        "# Usage\n" +
        "# docker run -d test/deploy\n" +
        "# \n" +
        "FROM ALPINE"
    )

class FakeCloneRepoImp(BaseDataFlowFacilitatorObjectContext):
    def __init__(self,*args,**kwargs):
        super().__init__()
    async def run(*args,**kwargs):
        print(f"\n\nRunning Fake clone repo\n\n")

        directory = tempfile.mkdtemp(prefix="test_deploy")
        with open(os.path.join(directory,"Dockerfile"),"w+") as dockerfile:
            dockerfile.write(DOCKERFILE_CONTENT)
        return {
            "repo":{"URL":"github.com/test/deploy",
            "directory":tempfile.mkdtemp(prefix="test_deploy")}
        }


class TestOperations(AsyncTestCase):
    async def setUp(self):
        self.test_inputs = {
                "TestRun":[
                    Input(
                        value={
                            "ref":"refs/master",
                            "repository":
                                {
                                    "clone_url":"https://github.com/test/deploy.git",
                                    "default_branch":"master",
                                    "html_url":"https://github.com/test/deploy"
                                }
                            },
                        definition=get_url_from_payload.op.inputs["payload"]
                    )
                ]
            }
    async def test_0_start_container(self):
        with mock.patch.object(clone_git_repo.imp,'CONTEXT',new = FakeCloneRepoImp):
            dataflow = DataFlow.auto(*OPIMPS)
            # dataflow.seed.append(
            #     Input(
            #         value=[get_url_from_payload.op.outputs["url"].name],
            #         definition=GetSingle.op.inputs["spec"]
            #     )
            # )
            async with MemoryOrchestrator.withconfig({}) as orchestrator:
                async with orchestrator(dataflow) as octx:
                    async for ctx, results in octx.run(self.test_inputs):
                        print(f"results:{results}")
                        # print(f"init_container : {self.init_container}")

    async def _1_test_restart_container(self):
        with mock.patch.object(clone_git_repo.imp.CONTEXT,'run',new = fake_clone_git_repo):
            dataflow = DataFlow.auto(*OPIMPS)
            dataflow.seed.append(
                Input(
                    value=[get_url_from_payload.op.outputs["url"].name],
                    definition=GetSingle.op.inputs["spec"]
                )
            )
            test_inputs = {
                "TestRun":[
                    Input(
                        value={
                            "ref": "refs/tags/simple-tag",
                            "deleted": True,
                            "forced": False,
                            "base_ref": None,
                            "repository":
                                {
                                    "clone_url":"github.com/test"
                                    }
                            } ,
                        definition=get_url_from_payload.op.inputs["payload"]
                    )
                ]
            }
            async with MemoryOrchestrator.withconfig({}) as orchestrator:
                async with orchestrator(dataflow) as octx:
                    async for ctx, results in octx.run(test_inputs):
                        print(f"results:{results}")
                        print(f"init_container : {self.init_container}")