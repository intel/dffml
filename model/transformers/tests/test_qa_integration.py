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
                        "qa",
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
                        "qa",
                        "test_data.sh",
                    ),
                ]
            )
            yield tempdir


class TestQAModel(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-transformers")
        # Generate sample data
        title = "World War 2"
        context = "Second world war lasted from 1939 to 1945. The first belligerent act of war was Germany's attack on Poland. The first two countries to declare war on Germany were Britain and France."
        train_ques_ans_list = [
            {
                "answers": [
                    {"answer_start": 18, "text": "lasted from 1939 to 1945"}
                ],
                "question": "How long was the second world war?",
                "id": "".join(
                    random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(10)
                ),
            },
            {
                "answers": [
                    {"answer_start": 164, "text": "Britain and France"}
                ],
                "question": "Which were the first two countries to declare war on Germany?",
                "id": "".join(
                    random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(10)
                ),
            },
            {
                "answers": [
                    {"answer_start": 81, "text": "Germany's attack on Poland"}
                ],
                "question": "What was the first act of war?",
                "id": "".join(
                    random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(10)
                ),
            },
        ]
        test_ques_ans_list = [
            {
                "answers": [{"answer_start": None, "text": None}],
                "question": "How long was the second world war?",
                "id": "".join(
                    random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(10)
                ),
            },
            {
                "answers": [{"answer_start": None, "text": None}],
                "question": "Which were the first two countries to declare war on Germany?",
                "id": "".join(
                    random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(10)
                ),
            },
            {
                "answers": [{"answer_start": None, "text": None}],
                "question": "What was the first act of war?",
                "id": "".join(
                    random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(10)
                ),
            },
        ]
        train_paragraphs = [{"context": context, "qas": train_ques_ans_list}]
        test_paragraphs = [{"context": context, "qas": test_ques_ans_list}]
        TRAIN_DATA = {
            "data": [{"title": title, "paragraphs": train_paragraphs}]
        }
        TEST_DATA = {"data": [{"title": title, "paragraphs": test_paragraphs}]}

        train_data_filename = self.mktempfile() + ".json"
        with open(pathlib.Path(train_data_filename), "w+") as data_file:
            json.dump(TRAIN_DATA, data_file)

        test_data_filename = self.mktempfile() + ".json"
        with open(pathlib.Path(test_data_filename), "w+") as data_file:
            json.dump(TEST_DATA, data_file)

        # Temp directory to be used for saving output and downloaded model
        directory = self.mktempdir()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "qa_model",
            "-sources",
            "s=op",
            "-source-opimp",
            "model.transformers.dffml_model_transformers.qa.utils:parser",
            "-source-args",
            train_data_filename,
            "True",
            "-log",
            "debug",
            "-model-model_type",
            "bert",
            "-model-model_name_or_path",
            "bert-base-cased",
            "-model-save_steps",
            "3",
            "-model-output_dir",
            directory,
            "-model-cache_dir",
            directory,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "qa_model",
            "-sources",
            "s=op",
            "-source-opimp",
            "model.transformers.dffml_model_transformers.qa.utils:parser",
            "-source-args",
            train_data_filename,
            "False",
            "-log",
            "debug",
            "-model-model_type",
            "bert",
            "-model-model_name_or_path",
            "bert-base-cased",
            "-model-save_steps",
            "3",
            "-model-output_dir",
            directory,
            "-model-cache_dir",
            directory,
        )
        with contextlib.redirect_stdout(self.stdout):
            # Make prediction
            await CLI._main(
                "predict",
                "all",
                "-model",
                "qa_model",
                "-sources",
                "s=op",
                "-source-opimp",
                "model.transformers.dffml_model_transformers.qa.utils:parser",
                "-source-args",
                test_data_filename,
                "False",
                "-log",
                "debug",
                "-model-model_type",
                "bert",
                "-model-model_name_or_path",
                "bert-base-cased",
                "-model-save_steps",
                "3",
                "-model-output_dir",
                directory,
                "-model-cache_dir",
                directory,
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
            results = [value for _, value in results.items()][0]
            self.assertIn(isinstance(results, str), [True])
            # Make prediction using dffml.operations.predict
            results = await Develop.cli(
                "run",
                "-log",
                "debug",
                "dffml.operation.model:model_predict",
                "-features",
                json.dumps(
                    {
                        "title": "World War 2",
                        "context": "Second world war lasted from 1939 to 1945. The first belligerent act of war was Germany's attack on Poland. The first two countries to declare war on Germany were Britain and France.",
                        "question": "How long was the second world war?",
                        "answer_text": "lasted from 1939 to 1945",
                        "start_pos_char": 18,
                        "is_impossible": False,
                        "id": "6667677676",
                        "answers": [],
                    }
                ),
                "-config-model",
                "qa_model",
                "-config-model-model_name_or_path",
                "bert-base-cased",
                "-config-model-output_dir",
                directory,
                "-config-model-cache_dir",
                directory,
                "-config-model-save_steps",
                "3",
                "-config-model-model_type",
                "bert",
            )
            self.assertIn("model_predictions", results)
            results = results["model_predictions"]
            self.assertIn("Answer", results)
            results = results["Answer"]
            self.assertIn("value", results)
            results = results["value"]
            results = [value for _, value in results.items()][0]
            self.assertIn(isinstance(results, str), [True])

        # Test .sh files
        def clean_args(fd, directory):
            cmnd = " ".join(fd.readlines()).split("\\\n")
            cmnd = " ".join(cmnd).split()
            for idx, word in enumerate(cmnd):
                cmnd[idx] = word.strip()
            cmnd[cmnd.index("-model-output_dir") + 1] = directory
            cmnd[cmnd.index("-model-cache_dir") + 1] = directory
            return cmnd

        with directory_with_csv_files() as tempdir:
            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "examples",
                    "qa",
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
                    "qa",
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
                    "qa",
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
                self.assertIn("Answer", results)
                results = results["Answer"]
                self.assertIn("value", results)
                results = results["value"]
                results = [value for _, value in results.items()][0]
                self.assertIn(isinstance(results, str), [True])
