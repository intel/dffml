import csv
import json
import random
import pathlib
import contextlib

from dffml.cli.cli import CLI
from dffml.util.asynctestcase import IntegrationCLITestCase


class TestNER(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-transformers")
        TRAIN_DATA = []
        PREDICT_DATA = []
        DATA_LEN = 1
        org_name = ["Tesla", "Facebook", "Nvidia", "Yahoo"]
        per_name = ["Walter", "Jack", "Sophia", "Ava"]
        loc_name = ["Germany", "India", "Australia", "Italy"]

        sentences = []
        for i in range(DATA_LEN):
            sentences.append(
                random.choice(per_name)
                + " "
                + random.choice(["works at", "joined", "left"])
                + " "
                + random.choice(org_name)
                + " "
                + random.choice(loc_name)
            )

        for id, sentence in enumerate(sentences):
            PREDICT_DATA.append([id, sentence])

        for id, sentence in enumerate(sentences):
            example = []
            words = sentence.split()
            for word in words:
                if word in org_name:
                    example.append([id, word, "I-ORG"])
                elif word in per_name:
                    example.append([id, word, "I-PER"])
                elif word in loc_name:
                    example.append([id, word, "I-LOC"])
                else:
                    example.append([id, word, "O"])
            TRAIN_DATA.extend(example)

        train_data_filename = self.mktempfile() + ".csv"
        predict_data_filename = (
            train_data_filename.split(".")[0] + "predict.csv"
        )

        with open(pathlib.Path(train_data_filename), "w+") as data_file:
            writer = csv.writer(data_file, delimiter=",")
            writer.writerow(["A", "B", "target"])
            writer.writerows(TRAIN_DATA)
        with open(pathlib.Path(predict_data_filename), "w+") as data_file:
            writer = csv.writer(data_file, delimiter=",")
            writer.writerow(["A", "B"])
            writer.writerows(PREDICT_DATA)

        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "ner_tagger",
            "-model-sid",
            "A:int:1",
            "-model-words",
            "B:str:1",
            "-model-predict",
            "target:str:1",
            "-model-model_architecture_type",
            "bert",
            "-model-model_name_or_path",
            "bert-base-cased",
            "-model-no_cuda",
            "-sources",
            "training_data=csv",
            "-log",
            "debug",
            "-source-filename",
            train_data_filename,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "ner_tagger",
            "-model-sid",
            "A:int:1",
            "-model-words",
            "B:str:1",
            "-model-predict",
            "target:str:1",
            "-model-model_architecture_type",
            "bert",
            "-model-model_name_or_path",
            "bert-base-cased",
            "-model-no_cuda",
            "-sources",
            "test_data=csv",
            "-log",
            "debug",
            "-source-filename",
            train_data_filename,
        )
        with contextlib.redirect_stdout(self.stdout):
            # Make prediction
            await CLI._main(
                "predict",
                "all",
                "-model",
                "ner_tagger",
                "-model-sid",
                "A:int:1",
                "-model-words",
                "B:str:1",
                "-model-predict",
                "target:str:1",
                "-model-model_architecture_type",
                "bert",
                "-model-model_name_or_path",
                "bert-base-cased",
                "-model-no_cuda",
                "-sources",
                "predict_data=csv",
                "-log",
                "debug",
                "-source-filename",
                predict_data_filename,
            )
            results = json.loads(self.stdout.getvalue())
            self.assertTrue(isinstance(results, list))
            self.assertTrue(results)
            results = results[0]
            self.assertIn("prediction", results)
            results = results["prediction"]
            self.assertIn("target", results)
            results = results["target"]
            self.assertIn("value", results)
            results = results["value"]
            self.assertTrue(results is not None)
