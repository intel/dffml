"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import os
import csv
import json
import random
import pathlib
import tempfile
import contextlib
import subprocess

from dffml.cli.cli import CLI
from dffml.util.os import chdir
from dffml.service.dev import Develop
from dffml.util.asynctestcase import IntegrationCLITestCase


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(
                [
                    "bash",
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        "examples",
                        "classification",
                        "train_data.sh",
                    ),
                ]
            )
            subprocess.check_output(
                [
                    "bash",
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        "examples",
                        "classification",
                        "test_data.sh",
                    ),
                ]
            )
            yield tempdir


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
        # Temp directory to be used for saving output, log and downloaded model
        directory = self.mktempdir()
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
            "-model-model_name_or_path",
            "bert-base-cased",
            "-model-output_dir",
            directory,
            "-model-cache_dir",
            directory,
            "-model-logging_dir",
            directory,
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
            "-model-model_name_or_path",
            "bert-base-cased",
            "-model-output_dir",
            directory,
            "-model-cache_dir",
            directory,
            "-model-logging_dir",
            directory,
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
                "-model-model_name_or_path",
                "bert-base-cased",
                "-model-output_dir",
                directory,
                "-model-cache_dir",
                directory,
                "-model-logging_dir",
                directory,
                "-sources",
                "predict_data=csv",
                "-source-filename",
                data_filename,
            )
            results = json.loads(self.stdout.getvalue())
            self.stdout.truncate(0)
            self.stdout.seek(0)
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
                "-config-model-model_name_or_path",
                "bert-base-cased",
                "-config-model-output_dir",
                directory,
                "-config-model-cache_dir",
                directory,
                "-config-model-logging_dir",
                directory,
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

        # Test .sh files
        def clean_args(fd, directory):
            cmnd = " ".join(fd.readlines()).split("\\\n")
            cmnd = " ".join(cmnd).split()
            for idx, word in enumerate(cmnd):
                cmnd[idx] = word.strip()
            cmnd[cmnd.index("-model-output_dir") + 1] = directory
            cmnd[cmnd.index("-model-cache_dir") + 1] = directory
            cmnd[cmnd.index("-model-logging_dir") + 1] = directory
            return cmnd

        with directory_with_csv_files() as tempdir:
            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "examples",
                    "classification",
                    "train.sh",
                ),
                "r",
            ) as f:
                train_cmnd = clean_args(f, tempdir)
            await CLI.cli(*train_cmnd[1:])

            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "examples",
                    "classification",
                    "accuracy.sh",
                ),
                "r",
            ) as f:
                accuracy_cmnd = clean_args(f, tempdir)
            await CLI.cli(*accuracy_cmnd[1:])

            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "examples",
                    "classification",
                    "predict.sh",
                ),
                "r",
            ) as f:
                predict_cmnd = clean_args(f, tempdir)
            with contextlib.redirect_stdout(self.stdout):
                await CLI._main(*predict_cmnd[1:])
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
