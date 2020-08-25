from random import randint

import numpy as np

from dffml.df.types import Input, DataFlow
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase

from dffml_operations_nlp.operations import (
    remove_stopwords,
    get_embedding,
    pos_tagger,
    lemmatizer,
    get_similarity,
    get_sentences,
    get_noun_chunks,
    count_vectorizer,
    tfidf_vectorizer,
)


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
        max_sentence_len = 15
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(get_embedding, GetSingle),
            [
                Input(
                    value=[get_embedding.op.outputs["embedding"].name],
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
                Input(
                    value=max_sentence_len,
                    definition=get_embedding.op.inputs["max_len"],
                ),
                Input(
                    value="<PAD>",
                    definition=get_embedding.op.inputs["pad_token"],
                ),
            ],
        ):
            embeddings = results[get_embedding.op.outputs["embedding"].name]
            self.assertEqual(max_sentence_len, len(embeddings))
            self.assertEqual(
                embeddings[randint(0, max_sentence_len - 1)].shape,
                embeddings[randint(0, max_sentence_len - 1)].shape,
            )

    async def test_pos_tagger(self):
        input_sentence = (
            "The end is the beginning , and the beginning is the end"
        )
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(pos_tagger, GetSingle),
            [
                Input(
                    value=[pos_tagger.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_sentence,
                    definition=pos_tagger.op.inputs["text"],
                ),
                Input(
                    value="en_core_web_sm",
                    definition=pos_tagger.op.inputs["spacy_model"],
                ),
            ],
        ):
            pos_tags = results[pos_tagger.op.outputs["result"].name]
            words = input_sentence.split()
            for i, _ in enumerate(words):
                self.assertEqual(pos_tags[i][0], words[i])
                self.assertIn(pos_tags[i][1], ["DT", "NN", "VBZ", "CC", ","])

    async def test_lemmatizer(self):
        input_sentence = (
            "The end is the beginning , and the beginning is the end"
        )
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(lemmatizer, GetSingle),
            [
                Input(
                    value=[lemmatizer.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_sentence,
                    definition=lemmatizer.op.inputs["text"],
                ),
                Input(
                    value="en_core_web_sm",
                    definition=lemmatizer.op.inputs["spacy_model"],
                ),
            ],
        ):
            lemma_list = results[lemmatizer.op.outputs["result"].name]
            self.assertEqual(len(input_sentence.split()), len(lemma_list))

    async def test_get_similarity(self):
        input_sentence1 = (
            "The end is the beginning , and the beginning is the end"
        )
        input_sentence2 = (
            "The end was the beginning , and the beginning was the end"
        )
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(get_similarity, GetSingle),
            [
                Input(
                    value=[get_similarity.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_sentence1,
                    definition=get_similarity.op.inputs["text_1"],
                ),
                Input(
                    value=input_sentence2,
                    definition=get_similarity.op.inputs["text_2"],
                ),
                Input(
                    value="en_core_web_sm",
                    definition=get_similarity.op.inputs["spacy_model"],
                ),
            ],
        ):
            similarity_score = results[
                get_similarity.op.outputs["result"].name
            ]
            self.assertGreater(similarity_score, 0.9)

    async def test_get_noun_chunks(self):
        input_sentence = (
            "The end is the beginning , and the beginning is the end"
        )
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(get_noun_chunks, GetSingle),
            [
                Input(
                    value=[get_noun_chunks.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_sentence,
                    definition=get_noun_chunks.op.inputs["text"],
                ),
                Input(
                    value="en_core_web_sm",
                    definition=get_noun_chunks.op.inputs["spacy_model"],
                ),
            ],
        ):
            noun_chunks = results[get_noun_chunks.op.outputs["result"].name]
            self.assertEqual(len(noun_chunks), 4)

    async def test_get_sentences(self):
        input_sentence = "The end is the beginning. The beginning is the end."
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(get_sentences, GetSingle),
            [
                Input(
                    value=[get_sentences.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_sentence,
                    definition=get_sentences.op.inputs["text"],
                ),
                Input(
                    value="en_core_web_sm",
                    definition=get_sentences.op.inputs["spacy_model"],
                ),
            ],
        ):
            sentences = results[get_sentences.op.outputs["result"].name]
            self.assertEqual(len(sentences), 2)

    async def test_count_vectorizer(self):
        input_sentence = [
            "The end is the beginning. The beginning is the end."
        ]
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(count_vectorizer, GetSingle),
            [
                Input(
                    value=[count_vectorizer.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_sentence,
                    definition=count_vectorizer.op.inputs["text"],
                ),
                Input(
                    value=[1, 1],
                    definition=count_vectorizer.op.inputs["ngram_range"],
                ),
                Input(
                    value=True,
                    definition=count_vectorizer.op.inputs["get_feature_names"],
                ),
            ],
        ):
            vectors = results[count_vectorizer.op.outputs["result"].name][0]
            features = results[count_vectorizer.op.outputs["result"].name][1]
            self.assertTrue(isinstance(features, list))
            self.assertTrue(isinstance(vectors, np.ndarray))
            unique_tokens = list(
                set(input_sentence[0].lower().replace(".", "").split())
            )
            self.assertEqual(len(vectors[0]), len(unique_tokens))
            self.assertEqual(
                set(features).intersection(set(unique_tokens)), set(features)
            )

    async def test_tfidf_vectorizer(self):
        input_sentence = [
            "The end is the beginning. The beginning is the end."
        ]
        async for ctx, results in MemoryOrchestrator.run(
            DataFlow.auto(tfidf_vectorizer, GetSingle),
            [
                Input(
                    value=[tfidf_vectorizer.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
                Input(
                    value=input_sentence,
                    definition=tfidf_vectorizer.op.inputs["text"],
                ),
                Input(
                    value=[1, 1],
                    definition=count_vectorizer.op.inputs["ngram_range"],
                ),
                Input(
                    value=True,
                    definition=tfidf_vectorizer.op.inputs["get_feature_names"],
                ),
            ],
        ):
            vectors = results[tfidf_vectorizer.op.outputs["result"].name][0]
            features = results[tfidf_vectorizer.op.outputs["result"].name][1]
            self.assertTrue(isinstance(features, list))
            self.assertTrue(isinstance(vectors, np.ndarray))
            unique_tokens = list(
                set(input_sentence[0].lower().replace(".", "").split())
            )
            self.assertEqual(len(vectors), len(unique_tokens))
            self.assertEqual(
                set(features).intersection(set(unique_tokens)), set(features)
            )
