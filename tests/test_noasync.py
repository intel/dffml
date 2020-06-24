"""
This file contains integration tests for the high level (very abstract) APIs.
"""
import importlib

from dffml.record import Record
from dffml.noasync import train, accuracy, predict
from dffml.source.csv import CSVSource
from dffml.feature.feature import Features, Feature
from dffml.util.asynctestcase import IntegrationCLITestCase

FEATURE_NAMES = ["Years", "Expertise", "Trust", "Salary"]


class TestML(IntegrationCLITestCase):
    async def populate_source(self, source_cls, *records, **kwargs):
        kwargs.setdefault("allowempty", True)
        kwargs.setdefault("readwrite", True)
        async with source_cls(**kwargs) as source:
            async with source() as sctx:
                for record in records:
                    await sctx.update(record)

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
            records = [
                Record(
                    i, data={"features": dict(zip(FEATURE_NAMES, features))}
                )
                for i, features in enumerate(getattr(self, f"{use}_data"))
            ]
            setattr(self, f"{use}_records", records)
            filename = self.mktempfile() + ".csv"
            setattr(self, f"{use}_filename", filename)
            await self.populate_source(CSVSource, *records, filename=filename)

    def test_predict(self):
        self.required_plugins("dffml-model-scikit")
        # Import SciKit modules
        dffml_model_scikit = importlib.import_module("dffml_model_scikit")
        # Instantiate the model
        model = dffml_model_scikit.LinearRegressionModel(
            directory=self.mktempdir(),
            predict=Feature("Salary", int, 1),
            features=Features(
                Feature("Years", int, 1),
                Feature("Expertise", int, 1),
                Feature("Trust", float, 1),
            ),
        )

        training_data = CSVSource(filename=self.train_filename)
        test_data = CSVSource(filename=self.test_filename)
        predict_data = CSVSource(filename=self.predict_filename)

        # Train the model
        train(model, training_data)
        # Assess accuracy
        accuracy(model, test_data)
        # Make prediction
        predictions = [
            prediction for prediction in predict(model, predict_data)
        ]
        self.assertEqual(round(predictions[0][2]["Salary"]["value"]), 70)
        self.assertEqual(round(predictions[1][2]["Salary"]["value"]), 80)
