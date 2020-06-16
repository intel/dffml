import random
import tempfile

from dffml.record import Record
from dffml.source.source import Sources
from dffml import train, accuracy, predict
from dffml.feature import Features, Feature
from dffml.util.asynctestcase import AsyncTestCase
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml_model_transformers.classification.classification_model import (
    HFClassificationModel,
    HFClassificationModelConfig,
)


class TestHFClassificationModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.features = Features()
        cls.features.append(Feature("A", str, 1))
        A, X = list(zip(*DATA))
        cls.records = [
            Record(str(i), data={"features": {"A": A[i], "X": X[i]}})
            for i in range(len(X))
        ]

        cls.sources = Sources(
            MemorySource(MemorySourceConfig(records=cls.records))
        )
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = HFClassificationModel(
            HFClassificationModelConfig(
                features=cls.features,
                predict=Feature("X", int, 1),
                label_list=["0", "1"],
            )
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        await train(self.model, self.sources)

    async def test_01_accuracy(self):
        res = await accuracy(self.model, self.sources)
        self.assertGreater(res, 0)

    async def test_02_predict(self):
        target_name = self.model.config.predict.name
        predictions = [
            prediction
            async for prediction in predict(self.model, self.sources)
        ]
        self.assertIn(predictions[0][2][target_name]["value"], ["0", "1"])
        self.assertIn(predictions[1][2][target_name]["value"], ["0", "1"])


# Randomly generate sample data
POSITIVE_WORDS = ["fun", "great", "cool", "awesome", "rad"]
NEGATIVE_WORDS = ["lame", "dumb", "silly", "stupid", "boring"]
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
    sentiment_words = random.choice(WORDS)
    sentiment_classification = WORDS.index(sentiment_words)
    DATA.append(
        [
            example.format(
                *random.sample(sentiment_words, example.count("{}"))
            ),
            str(sentiment_classification),
        ]
    )
