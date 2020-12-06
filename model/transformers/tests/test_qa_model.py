import tempfile

from dffml.record import Record
from dffml.source.source import Sources
from dffml import train, accuracy, predict
from dffml.util.asynctestcase import AsyncTestCase
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml_model_transformers.qa.qa_model import QAModel, QAModelConfig

from .defaults import CACHE_DIR


class TestQAModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        (A_train, B_train, C_train, X_train, D_train, E_train,) = list(
            zip(*TRAIN_DATA)
        )
        A_test, B_test, C_test, X_test, D_test, E_test = list(zip(*TEST_DATA))

        cls.train_records = [
            Record(
                str(i),
                data={
                    "features": {
                        "title": A_train[i],
                        "context": B_train[i],
                        "question": C_train[i],
                        "answer_text": X_train[i],
                        "start_pos_char": D_train[i],
                        "is_impossible": E_train[i],
                        "answers": [],
                    }
                },
            )
            for i in range(len(X_train))
        ]
        cls.test_records = [
            Record(
                str(i),
                data={
                    "features": {
                        "title": A_test[i],
                        "context": B_test[i],
                        "question": C_test[i],
                        "answer_text": X_test[i],
                        "start_pos_char": D_test[i],
                        "is_impossible": E_test[i],
                        "answers": [],
                    }
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
        cls.model = QAModel(
            QAModelConfig(
                model_name_or_path="bert-base-cased",
                cache_dir=CACHE_DIR,
                directory=cls.model_dir.name,
                log_dir=cls.model_dir.name,
                model_type="bert",
                no_cuda=True,
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

        self.assertIn(
            isinstance(predictions[0][2]["Answer"]["value"]["0"], str), [True]
        )
        self.assertIn(
            isinstance(predictions[1][2]["Answer"]["value"]["1"], str), [True]
        )


# Randomly generate sample data
title = "World War 2"
context = "Second world war lasted from 1939 to 1945. The first belligerent act of war was Germany's attack on Poland. The first two countries to declare war on Germany were Britain and France."
# train_ques_ans_list = [[question, answer_text, start_pos_char, is_impossible]]
train_ques_ans_list = [
    [
        "How long was the second world war?",
        "lasted from 1939 to 1945",
        18,
        False,
    ],
    [
        "Which were the first two countries to declare war on Germany?",
        "Britain and France",
        164,
        False,
    ],
    [
        "What was the first act of war?",
        "Germany's attack on Poland",
        81,
        False,
    ],
]
test_ques_ans_list = [
    ["How long was the second world war?", " ", 0, False,],
    [
        "Which were the first two countries to declare war on Germany?",
        " ",
        0,
        False,
    ],
    ["What was the first act of war?", " ", 0, False,],
]
TRAIN_DATA = [[title, context, *d] for d in train_ques_ans_list]
TEST_DATA = [[title, context, *d] for d in test_ques_ans_list]
