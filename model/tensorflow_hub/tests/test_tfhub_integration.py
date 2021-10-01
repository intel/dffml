"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import csv
import json
import random
import pathlib

from dffml.cli.cli import CLI
from dffml.service.dev import Develop
from dffml.util.asynctestcase import AsyncTestCase


class TestTextClassifier(AsyncTestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-tensorflow-hub")
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

        model_dir = self.mktempdir()

        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "text_classifier",
            *features,
            "-model-predict",
            "sentiment:int:1",
            "-model-location",
            model_dir,
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
            "-model-location",
            model_dir,
            "-model-classifications",
            "0",
            "1",
            "-model-clstype",
            "int",
            "-features",
            "sentiment:int:1",
            "-sources",
            "test_data=csv",
            "-source-filename",
            data_filename,
            "-scorer",
            "textclf",
        )
        # Make prediction
        results = await CLI._main(
            "predict",
            "all",
            "-model",
            "text_classifier",
            *features,
            "-model-predict",
            "sentiment:int:1",
            "-model-location",
            model_dir,
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
        self.assertTrue(isinstance(results, list))
        self.assertTrue(results)
        results = results[0].export()
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
            "text_classifier",
            "-config-model-features",
            "text:str:1",
            "-config-model-predict",
            "sentiment:int:1",
            "-config-model-location",
            model_dir,
            "-config-model-classifications",
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
