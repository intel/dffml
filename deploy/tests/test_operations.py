import sys

from dffml.df.types import Input, DataFlow
from dffml.df.base import opimp_in
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from deploy.operations import get_payload,get_url_from_payload



class TestOperations(AsyncTestCase):
    async def test_get_url(self):
        dataflow = DataFlow.auto(GetSingle,get_payload,get_url_from_payload)
        dataflow.seed.append(
            Input(
                value=[get_url_from_payload.op.outputs["url"].name],
                definition=GetSingle.op.inputs["spec"]
            )
        )
        test_inputs = {
            "TestGetUrl":[
                Input(
                    value='{ "ref": "refs/tags/simple-tag","deleted": true,"forced": false,"base_ref": null,"repository":{"clone_url":"github.com/test"}}' ,
                    definition=get_payload.op.inputs["payload_str"]
                )
            ]
        }
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(test_inputs):
                    print(f"results:{results}")