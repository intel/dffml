import io
import unittest.mock
import json

from dffml.df.types import DataFlow, Input
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.dfrepos import run_dataflow_on_repo,RunDataFlowOnRepoConfig
from dffml.operation.output import GetSingle
from tests.integration.common import IntegrationCLITestCase,relative_chdir
from dffml.service.dev import Develop

from shouldi.safety import safety_check
from shouldi.bandit import run_bandit
from dffml.df.base import OperationImplementationContext
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
                operations={"run_on_repos":run_dataflow_on_repo.op,
                                "get_single":GetSingle.imp.op },
                configs={ "run_on_repos":RunDataFlowOnRepoConfig(shouldi_dataflow) },
                seed=[ 
                        Input(
                            value=[ run_dataflow_on_repo.op.outputs["results"].name ],
                            definition=GetSingle.op.inputs["spec"],
                            )
                    ],
                )
        
        test_ins = [
                    {"insecure_package":[
                                    {
                                    "value":"insecure-package",
                                    "definition":"package"
                                    }
                                ]
                    },
                    {"dffml":[
                                    {
                                    "value":"dffml",
                                    "definition":"package"
                                    }
                                ]
                    }
                    ]
        test_outs = {
                    "insecure_package" : 
                    {
                        'safety_check_number_of_issues': 1, 
                        'bandit_output': 
                            {'CONFIDENCE.HIGH': 0.0, 'CONFIDENCE.LOW': 0.0, 
                                'CONFIDENCE.MEDIUM': 0.0, 'CONFIDENCE.UNDEFINED': 0.0, 
                                'SEVERITY.HIGH': 0.0, 'SEVERITY.LOW': 0.0, 'SEVERITY.MEDIUM': 0.0, 
                                'SEVERITY.UNDEFINED': 0.0, 'loc': 100, 'nosec': 0, 
                                'CONFIDENCE.HIGH_AND_SEVERITY.HIGH': 0
                            }
                    },

                    "dffml": {'safety_check_number_of_issues': 0, 
                            'bandit_output': 
                                {'CONFIDENCE.HIGH': 20.0, 'CONFIDENCE.LOW': 0.0, 
                                    'CONFIDENCE.MEDIUM': 0.0, 'CONFIDENCE.UNDEFINED': 0.0, 
                                    'SEVERITY.HIGH': 0.0, 'SEVERITY.LOW': 9.0, 'SEVERITY.MEDIUM': 11.0,
                                    'SEVERITY.UNDEFINED': 0.0, 'loc': 9705, 'nosec': 0,
                                     'CONFIDENCE.HIGH_AND_SEVERITY.HIGH': 0
                                }
                            }
                            
                }
        
        

        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(test_dataflow) as octx:
                async for _ctx, results in octx.run(
                    {
                            list(test_in.keys())[0] : [
                                    Input(
                                        value=test_in,
                                        definition=run_dataflow_on_repo.op.inputs["ins"],
                                        ),
                                ]  for test_in in test_ins
                    }
                ):
                    ctx_str = (await _ctx.handle()).as_string()
                    self.assertIn("flow_results",results)
                    out=results["flow_results"]
                    self.assertIn(ctx_str,list(map(str,out.keys())))
                    self.assertIn(ctx_str,test_outs)
                    expected = test_outs[ctx_str]
                    out=list(out.values())[0]
                    self.assertEqual(expected,out)



        

