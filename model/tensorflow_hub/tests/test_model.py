import sys
import random
import tempfile
from typing import Type

from dffml.repo import Repo, RepoData
from dffml.source.source import Sources
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature import Data, Feature, Features, DefFeature
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
                classifications=["a", "not a"],
                features=cls.features,
                predict=DefFeature("X", str, 1),
                # layers=[
                #     "Dense(16, activation='relu')",
                #     "Dense(1, activation='sigmoid')",
                # ],
                model_path="/home/himanshu/Downloads/1 (3) (1)",
                modelArchitecture="bert",
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
            async with sources() as sctx, model() as mctx:
                async for repo in mctx.predict(sctx.repos()):
                    prediction = repo.prediction().value
                    self.assertIn(prediction, ["a", "not a"])


DATA = [
    ["my name is himanshu", "a"],
    ["where do you live", "not a"],
    ["hi", "a"],
]

test_cls = type(
    f"TestTextClassificationModel",
    (TestTextClassificationModel, AsyncTestCase),
    {"MODEL_TYPE": "TextClassification",},
)
setattr(sys.modules[__name__], test_cls.__qualname__, test_cls)
