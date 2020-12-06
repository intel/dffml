import random
import tempfile

from dffml.record import Record
from dffml.source.source import Sources
from dffml import train, accuracy, predict, run_consoletest
from dffml.util.asynctestcase import AsyncTestCase
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml_model_spacy.ner.ner_model import SpacyNERModel, SpacyNERModelConfig


class TestSpacyNERModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        A_train, X_train = list(zip(*TRAIN_DATA))
        A_test, X_test = list(zip(*TEST_DATA))

        cls.train_records = [
            Record(
                str(i),
                data={
                    "features": {
                        "sentence": A_train[i],
                        "entities": X_train[i],
                    }
                },
            )
            for i in range(len(X_train))
        ]
        cls.test_records = [
            Record(
                str(i),
                data={
                    "features": {"sentence": A_test[i], "entities": X_test[i],}
                },
            )
            for i in range(len(X_test))
        ]

        cls.train_sources = Sources(
            MemorySource(MemorySourceConfig(records=cls.train_records))
        )
        cls.test_sources = Sources(
            MemorySource(MemorySourceConfig(records=cls.test_records))
        )
        cls.model_dir = tempfile.TemporaryDirectory()
        cls.model = SpacyNERModel(
            SpacyNERModelConfig(
                model_name_or_path="en_core_web_sm",
                directory=cls.model_dir.name,
                n_iter=10,
                dropout=0.4,
            )
        )

    @classmethod
    def tearDownClass(cls):
        cls.model_dir.cleanup()

    async def test_00_train(self):
        await train(self.model, self.train_sources)

    async def test_01_accuracy(self):
        res = await accuracy(self.model, self.train_sources)
        self.assertGreaterEqual(res, 0)

    async def test_02_predict(self):
        predictions = [
            prediction
            async for prediction in predict(self.model, self.test_sources)
        ]
        self.assertTrue(
            isinstance(predictions[0][2]["Tag"]["value"][0], tuple)
        )
        self.assertIn(
            predictions[0][2]["Tag"]["value"][0][1], ["ORG", "PERSON", "LOC"]
        )

    async def test_docstring(self):
        await run_consoletest(SpacyNERModel)


TRAIN_DATA = []
TEST_DATA = []
all_data = [
    ["I went to switzerland.", [(10, 21, "LOC")]],
    ["I like India and Japan.", [(7, 12, "LOC"), (17, 22, "LOC")]],
    ["Who is Albert Einstein?", [(7, 22, "PERSON")]],
    ["World needs Nikola Tesla.", [(12, 24, "PERSON")]],
]

train_data_idx = random.sample(range(0, len(all_data) - 1), 3)

for i in train_data_idx:
    TRAIN_DATA.append(all_data[i])

for i in range(len(all_data)):
    if i not in train_data_idx:
        TEST_DATA.append(all_data[i])
