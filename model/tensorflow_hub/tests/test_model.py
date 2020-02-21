import random
import tempfile

from dffml.repo import Repo
from dffml.source.source import Sources
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature import Features, DefFeature
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml_model_tensorflow_hub.text_classifier import (
    TextClassificationModel,
    TextClassifierConfig,
)


class TestTextClassificationModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.features = Features()
        cls.features.append(DefFeature("A", str, 1))
        A, X = list(zip(*DATA))
        cls.repos = [
            Repo(str(i), data={"features": {"A": A[i], "X": X[i],}},)
            for i in range(0, len(X))
        ]
        cls.sources = Sources(
            MemorySource(MemorySourceConfig(repos=cls.repos))
        )
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = TextClassificationModel(
            TextClassifierConfig(
                directory=cls.model_dir.name,
                classifications=[0, 1],
                features=cls.features,
                predict=DefFeature("X", int, 1),
                add_layers=True,
                layers=[
                    "Dense(units = 120, activation='relu')",
                    "Dense(units = 64, activation=relu)",
                    "Dense(units = 2, activation='softmax')",
                ],
                model_path="https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim-with-oov/1",
                epochs=30,
            )
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                await mctx.train(sctx)

    async def test_01_accuracy(self):
        async with self.sources as sources, self.model as model:
            async with sources() as sctx, model() as mctx:
                res = await mctx.accuracy(sctx)
                self.assertGreater(res, 0)

    async def test_02_predict(self):
        async with self.sources as sources, self.model as model:
            target_name = model.config.predict.NAME
            async with sources() as sctx, model() as mctx:
                async for repo in mctx.predict(sctx.repos()):
                    prediction = repo.prediction(target_name).value
                    self.assertIn(prediction, ["0", "1"])


# Randomly generate sample data
POSITIVE_WORDS = [
    "fun",
    "great",
    "cool",
    "awesome",
    "rad",
]
NEGATIVE_WORDS = [
    "lame",
    "dumb",
    "silly",
    "stupid",
    "boring",
]
WORDS = [NEGATIVE_WORDS, POSITIVE_WORDS]

SENTENCES = [
    "I think my dog is {}",
    "That cat is {}",
    "Potatoes are {}",
    "When I lived in Wisconsin I felt that it was {}",
    "I think differential equations are {}",
]

DATA = []

for example in SENTENCES:
    sentement_words = random.choice(WORDS)
    sentement_classification = WORDS.index(sentement_words)
    DATA.append(
        [
            example.format(
                *random.sample(sentement_words, example.count("{}"))
            ),
            str(sentement_classification),
        ]
    )
