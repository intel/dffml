from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase
from dffml.df.types import DataFlow, Input, Definition
from dffml.operation.output import AssociateDefinition


class TestAssociateDefinition(AsyncTestCase):
    async def test_associatedefinition(self):
        feed_def = Definition(name="feed", primitive="string")
        dead_def = Definition(name="dead", primitive="string")
        output = Definition(name="output", primitive="string")

        feed_input = Input(value="my favorite value", definition=feed_def)
        face_input = Input(
            value="face", definition=output, parents=[feed_input]
        )

        dead_input = Input(
            value="my second favorite value", definition=dead_def
        )
        beef_input = Input(
            value="beef", definition=output, parents=[dead_input]
        )

        test_result = {"feed": "face", "dead": "beef"}
        for test_value in test_result.keys():
            async for ctx, results in MemoryOrchestrator.run(
                DataFlow.auto(AssociateDefinition),
                [
                    feed_input,
                    face_input,
                    dead_input,
                    beef_input,
                    Input(
                        value={test_value: "output"},
                        definition=AssociateDefinition.op.inputs["spec"],
                    ),
                ],
            ):
                self.assertEqual(
                    results, {test_value: test_result[test_value]}
                )
