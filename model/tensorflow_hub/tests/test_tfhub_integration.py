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
from dffml.util.asynctestcase import IntegrationCLITestCase


class TestTextClassifier(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-tensorflow-hub")
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
            "text_classifier",
            *features,
            "-model-predict",
            "sentiment:int:1",
            "-model-classifications",
            "0",
            "1",
            "-model-clstype",
            "int",
            "-sources",
            "training_data=csv",
            "-source-filename",
            data_filename,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "text_classifier",
            *features,
            "-model-predict",
            "sentiment:int:1",
            "-model-classifications",
            "0",
            "1",
            "-model-clstype",
            "int",
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
                "text_classifier",
                *features,
                "-model-predict",
                "sentiment:int:1",
                "-model-classifications",
                "0",
                "1",
                "-model-clstype",
                "int",
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
