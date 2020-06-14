"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import csv
import json
import random
import pathlib
import contextlib

from dffml.cli.cli import CLI
from dffml.service.dev import Develop
from dffml.util.asynctestcase import IntegrationCLITestCase


class TestHFClassifier(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-transformers")
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
        data_filename = self.mktempfile() + ".csv"
        with open(pathlib.Path(data_filename), "w+") as data_file:
            writer = csv.writer(data_file, delimiter=",")
            writer.writerow(["text", "sentiment"])
            writer.writerows(DATA)

        # Features
        features = "-model-features text:str:1".split()

        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "hfclassifier",
            *features,
            "-model-predict",
            "sentiment:int:1",
            "-model-clstype",
            "int",
            "-model-label_list",
            "0",
            "1",
            "-sources",
            "training_data=csv",
            "-source-filename",
            data_filename,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "hfclassifier",
            *features,
            "-model-predict",
            "sentiment:int:1",
            "-model-clstype",
            "int",
            "-model-label_list",
            "0",
            "1",
            "-sources",
            "test_data=csv",
            "-source-filename",
            data_filename,
        )
        with contextlib.redirect_stdout(self.stdout):
            # Make prediction
            await CLI._main(
                "predict",
                "all",
                "-model",
                "hfclassifier",
                *features,
                "-model-predict",
                "sentiment:int:1",
                "-model-clstype",
                "int",
                "-model-label_list",
                "0",
                "1",
                "-sources",
                "predict_data=csv",
                "-source-filename",
                data_filename,
            )
            results = json.loads(self.stdout.getvalue())
            self.assertTrue(isinstance(results, list))
            self.assertTrue(results)
            results = results[0]
            self.assertIn("prediction", results)
            results = results["prediction"]
            self.assertIn("sentiment", results)
            results = results["sentiment"]
            self.assertIn("value", results)
            results = results["value"]
            self.assertIn(results, [0, 1])

            # Make prediction using dffml.operations.predict
            results = await Develop.cli(
                "run",
                "-log",
                "debug",
                "dffml.operation.model:model_predict",
                "-features",
                json.dumps({"text": "My dog is awesome"}),
                "-config-model",
                "hfclassifier",
                "-config-model-features",
                "text:str:1",
                "-config-model-predict",
                "sentiment:int:1",
                "-config-model-label_list",
                "0",
                "1",
                "-config-model-clstype",
                "int",
            )
            self.assertIn("model_predictions", results)
            results = results["model_predictions"]
            self.assertIn("sentiment", results)
            results = results["sentiment"]
            self.assertIn("value", results)
            results = results["value"]
            self.assertIn(results, [0, 1])
