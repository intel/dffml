"""
This file contains integration tests for the high level (very abstract) APIs.
"""
import importlib

from dffml.repo import Repo
from dffml import train, accuracy, predict
from dffml.source.csv import CSVSource
from dffml.feature.feature import Features, DefFeature
from dffml.util.asynctestcase import IntegrationCLITestCase

FEATURE_NAMES = ["Years", "Expertise", "Trust", "Salary"]


class TestML(IntegrationCLITestCase):
    async def populate_source(self, source_cls, *repos, **kwargs):
        kwargs.setdefault("allowempty", True)
        kwargs.setdefault("readwrite", True)
        async with source_cls(**kwargs) as source:
            async with source() as sctx:
                for repo in repos:
                    await sctx.update(repo)

    async def setUp(self):
        await super().setUp()
        self.train_data = [
            [0, 1, 0.2, 10],
            [1, 3, 0.4, 20],
            [2, 5, 0.6, 30],
            [3, 7, 0.8, 40],
        ]
        self.test_data = [[4, 9, 1.0, 50], [5, 11, 1.2, 60]]
        self.predict_data = [[6, 13, 1.4], [7, 15, 1.6]]
        for use in ["train", "test", "predict"]:
            repos = [
                Repo(i, data={"features": dict(zip(FEATURE_NAMES, features))})
                for i, features in enumerate(getattr(self, f"{use}_data"))
            ]
            setattr(self, f"{use}_repos", repos)
            filename = self.mktempfile() + ".csv"
            setattr(self, f"{use}_filename", filename)
            await self.populate_source(CSVSource, *repos, filename=filename)

    async def test_predict(self):
        self.required_plugins("dffml-model-scikit")
        # Import SciKit modules
        dffml_model_scikit = importlib.import_module("dffml_model_scikit")
        # Instantiate the model
        model = dffml_model_scikit.LinearRegressionModel(
            directory=self.mktempdir(),
            predict=DefFeature("Salary", int, 1),
            features=Features(
                DefFeature("Years", int, 1),
                DefFeature("Expertise", int, 1),
                DefFeature("Trust", float, 1),
            ),
        )

        training_data = CSVSource(filename=self.train_filename)
        test_data = CSVSource(filename=self.test_filename)
        predict_data = CSVSource(filename=self.predict_filename)

        # Train the model
        await train(model, training_data)
        # Assess accuracy
        await accuracy(model, test_data)
        # Make prediction
        predictions = [
            prediction async for prediction in predict(model, predict_data)
        ]
        self.assertEqual(predictions[0][2]["Salary"]["value"], 70)
        self.assertEqual(predictions[1][2]["Salary"]["value"], 80)
