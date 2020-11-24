import os
import random
import pathlib
import tempfile

from dffml import accuracy
from dffml.record import Record
from dffml.source.source import Sources
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature import Feature
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.accuracy import ClassificationAccuracy
from dffml_model_transformers.ner.ner_model import NERModel, NERModelConfig


class TestNERModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        A_train, B_train, X = list(zip(*TRAIN_DATA))
        A_predict, B_predict = list(zip(*PREDICT_DATA))

        cls.train_records = [
            Record(
                str(i),
                data={
                    "features": {
                        "sentence_id": A_train[i],
                        "words": B_train[i],
                        "ner_tag": X[i],
                    }
                },
            )
            for i in range(len(X))
        ]
        cls.train_sources = Sources(
            MemorySource(MemorySourceConfig(records=cls.train_records))
        )

        cls.predict_records = [
            Record(
                str(i),
                data={
                    "features": {
                        "sentence_id": A_predict[i],
                        "words": B_predict[i],
                    }
                },
            )
            for i in range(len(A_predict))
        ]
        cls.predict_sources = Sources(
            MemorySource(MemorySourceConfig(records=cls.predict_records))
        )

        cls.model_dir = tempfile.TemporaryDirectory()
        cls.cache_dir = tempfile.TemporaryDirectory()
        cls.model = NERModel(
            NERModelConfig(
                sid=Feature("sentence_id", int, 1),
                words=Feature("words", str, 1),
                predict=Feature("ner_tag", str, 1),
                output_dir=cls.model_dir.name,
                model_name_or_path="bert-base-cased",
                no_cuda=True,
                cache_dir=cls.cache_dir.name,
            )
        )
        cls.scorer = ClassificationAccuracy()

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()
        cls.cache_dir.cleanup()

    async def test_00_train(self):
        async with self.train_sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        res = await accuracy(self.model, self.scorer, self.train_sources)
        self.assertTrue(res >= 0)

    async def test_02_predict(self):
        async with self.predict_sources as sources, self.model as model:
            target_name = model.config.predict.name
            async with sources() as sctx, model() as mctx:
                async for record in mctx.predict(sctx):
                    prediction = record.prediction(target_name).value
                    for d in prediction:
                        self.assertIn(
                            list(d.values())[0],
                            [
                                "O",
                                "B-MISC",
                                "I-MISC",
                                "B-PER",
                                "I-PER",
                                "B-ORG",
                                "I-ORG",
                                "B-LOC",
                                "I-LOC",
                            ],
                        )


TRAIN_DATA = []
PREDICT_DATA = []
DATA_LEN = 20
org_name = ["Tesla", "Facebook", "Nvidia", "Yahoo"]
per_name = ["Walter", "Jack", "Sophia", "Ava"]
loc_name = ["Germany", "India", "Australia", "Italy"]

sentences = [
    random.choice(per_name)
    + " "
    + random.choice(["works at", "joined", "left"])
    + " "
    + random.choice(org_name)
    + " "
    + random.choice(loc_name)
    for _ in range(DATA_LEN)
]
for id, sentence in enumerate(sentences):
    PREDICT_DATA.append([id, sentence])

for id, sentence in enumerate(sentences):
    example = []
    words = sentence.split()
    for word in words:
        if word in org_name:
            example.append([id, word, "I-ORG"])
        elif word in per_name:
            example.append([id, word, "I-PER"])
        elif word in loc_name:
            example.append([id, word, "I-LOC"])
        else:
            example.append([id, word, "O"])
    TRAIN_DATA.extend(example)
