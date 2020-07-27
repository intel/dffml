"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import os
import csv
import json
import random
import string
import pathlib
import tempfile
import contextlib
import subprocess

from dffml.cli.cli import CLI
from dffml.util.os import chdir
from dffml.service.dev import Develop
from dffml.util.asynctestcase import IntegrationCLITestCase


class TestSpacyNERModel(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-spacy")
        # Generate sample data
        TRAIN_DATA = []
        TEST_DATA = []
        FORMATTED_DATA = []
        RAW_DATA = [
            ["I went to switzerland.", [(10, 21, "LOC")]],
            ["I like India and Japan.", [(7, 12, "LOC"), (17, 22, "LOC")]],
            ["Who is Albert Einstein?", [(7, 22, "PERSON")]],
            ["World needs Nikola Tesla.", [(12, 24, "PERSON")]],
        ]

        for example in RAW_DATA:
            text, annotation = example
            entities = []
            for ent in annotation:
                entity = {}
                entity["start"] = ent[0]
                entity["end"] = ent[1]
                entity["tag"] = ent[2]
                entities.append(entity)
            FORMATTED_DATA.append({"sentence": text, "entities": entities})

        train_data_idx = random.sample(range(0, len(RAW_DATA) - 1), 3)

        for i in train_data_idx:
            TRAIN_DATA.append(FORMATTED_DATA[i])

        for i in range(len(RAW_DATA)):
            if i not in train_data_idx:
                TEST_DATA.append(FORMATTED_DATA[i])
        TRAIN_DATA = {"data": TRAIN_DATA}
        TEST_DATA = {"data": TEST_DATA}

        train_data_filename = self.mktempfile() + ".json"
        with open(pathlib.Path(train_data_filename), "w+") as data_file:
            json.dump(TRAIN_DATA, data_file)

        test_data_filename = self.mktempfile() + ".json"
        with open(pathlib.Path(test_data_filename), "w+") as data_file:
            json.dump(TEST_DATA, data_file)

        # Temp directory to be used for saving output
        directory = self.mktempdir()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "spacyner",
            "-sources",
            "s=op",
            "-source-opimp",
            "model.spacy.dffml_model_spacy.ner.utils:parser",
            "-source-args",
            train_data_filename,
            "False",
            "-log",
            "debug",
            "-model-model_name_or_path",
            "en_core_web_sm",
            "-model-output_dir",
            directory,
            "-model-n_iter",
            "5",
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "spacyner",
            "-sources",
            "s=op",
            "-source-opimp",
            "model.spacy.dffml_model_spacy.ner.utils:parser",
            "-source-args",
            train_data_filename,
            "False",
            "-log",
            "debug",
            "-model-model_name_or_path",
            "en_core_web_sm",
            "-model-output_dir",
            directory,
            "-model-n_iter",
            "5",
        )
        with contextlib.redirect_stdout(self.stdout):
            # Make prediction
            await CLI._main(
                "predict",
                "all",
                "-model",
                "spacyner",
                "-sources",
                "s=op",
                "-source-opimp",
                "model.spacy.dffml_model_spacy.ner.utils:parser",
                "-source-args",
                test_data_filename,
                "True",
                "-log",
                "debug",
                "-model-model_name_or_path",
                "en_core_web_sm",
                "-model-output_dir",
                directory,
                "-model-n_iter",
                "5",
            )
            results = json.loads(self.stdout.getvalue())
            self.stdout.truncate(0)
            self.stdout.seek(0)
            self.assertTrue(isinstance(results, list))
            self.assertTrue(results)
            results = results[0]
            self.assertIn("prediction", results)
            results = results["prediction"]
            self.assertIn("Answer", results)
            results = results["Answer"]
            self.assertIn("value", results)
            results = results["value"]
            self.assertIn(results[0][1], ["ORG", "PERSON"])

        # Make prediction using dffml.operations.predict
        result = await Develop.cli(
            "run",
            "-log",
            "debug",
            "dffml.operation.model:model_predict",
            "-features",
            json.dumps(
                {
                    "sentence": "Alber Einstein was really really smart.",
                    "entities": [],
                }
            ),
            "-config-model",
            "spacyner",
            "-config-model-model_name_or_path",
            "en_core_web_sm",
            "-config-model-output_dir",
            directory,
        )
        self.assertIn("model_predictions", result)
        result = result["model_predictions"]
        self.assertIn("Answer", result)
        result = result["Answer"]
        self.assertIn("value", result)
        result = result["value"]
        self.assertIn(result[0][1], ["ORG", "PERSON"])
