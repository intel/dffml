import io
import unittest.mock
import json

from dffml.df.types import DataFlow, Input
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle


from dffml.operation.dfrepos import run_dataflow_on_repo,RunDataFlowOnRepoConfig
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase
from tests.integration.common import IntegrationCLITestCase,relative_chdir
from dffml.service.dev import Develop

from shouldi.safety import safety_check
from shouldi.bandit import run_bandit

class TestRunDataFlowOnRepo(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("shouldi")
        stdout = io.StringIO()

        with relative_chdir("..", "..", "examples", "shouldi"):
            with unittest.mock.patch("sys.stdout.buffer.write") as write:
                await Develop.cli("export", "shouldi.cli:DATAFLOW")
            shouldi_dataflow = DataFlow._fromdict(**json.loads(write.call_args[0][0]))
        
        shouldi_dataflow.seed.append(
                            Input(
                                value=[
                                    safety_check.op.outputs["issues"].name,
                                    run_bandit.op.outputs["report"].name,
                                ],
                                definition=GetSingle.op.inputs["spec"],
                            )
                        )
        
        test_dataflow = DataFlow(
                operations={"run_on_repos":run_dataflow_on_repo.op},
                configs={ "run_on_repos":{"dataflow":shouldi_dataflow} },
                seed=[ 
                        Input(
                            value=[ run_dataflow_on_repo.op.outputs["results"].name ],
                            definition=GetSingle.op.inputs["spec"],
                            )
                    ],
                )
        
        test_ins = [
                    {"test_insecure_package":[
                                    {
                                    "value":"insecure-package",
                                    "definition":"package"
                                    }
                                ]
                    },
                    ]
        
        

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(test_dataflow) as octx:
                async for ctx_str, results in octx.run(
                    {
                            test_in.keys()[0] : [
                                    Input(
                                        value=test_in,
                                        definition=run_dataflow_on_repo.op.inputs["flow_ins"],
                                        )
                                ] for test_in in test_ins
                    }
                ):
                    print(results)

        

