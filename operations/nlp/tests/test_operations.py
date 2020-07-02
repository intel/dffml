from random import randint

from dffml.df.types import Input, DataFlow
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operations_nlp.operations import remove_stopwords, get_embedding


class TestOperations(AsyncTestCase):
    async def test_remove_stopwords(self):
        input_sentence = (
            "The end is the beginning, and the beginning is the end"
        )
        output_sentence = "end beginning , beginning end"
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(remove_stopwords, GetSingle),
            [
                Input(
                    value=[remove_stopwords.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_sentence,
                    definition=remove_stopwords.op.inputs["text"],
                ),
            ],
        ):
            self.assertEqual(
                results[remove_stopwords.op.outputs["result"].name],
                output_sentence,
            )

    async def test_get_embedding(self):
        input_sentence = (
            "The end is the beginning , and the beginning is the end"
        )
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(get_embedding, GetSingle),
            [
                Input(
                    value=[get_embedding.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_sentence,
                    definition=get_embedding.op.inputs["text"],
                ),
                Input(
                    value="en_core_web_sm",
                    definition=get_embedding.op.inputs["spacy_model"],
                ),
            ],
        ):
            embeddings = results[get_embedding.op.outputs["result"].name]
            self.assertEqual(len(input_sentence.split()), len(embeddings))
            self.assertEqual(
                embeddings[randint(0, len(input_sentence.split()) - 1)].shape,
                embeddings[randint(0, len(input_sentence.split()) - 1)].shape,
            )
