"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import csv
import json
import inspect
import pathlib
import contextlib

import numpy as np
from sklearn.datasets import make_classification

from dffml.cli.cli import CLI
from dffml.util.asynctestcase import IntegrationCLITestCase


class TestVWModel(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-vowpalWabbit")
        # Create the training data
        data_filename = self.mktempfile() + ".csv"
        X, y = make_classification(
            n_samples=10,
            n_features=5,
            n_classes=2,
            n_informative=3,
            shuffle=True,
            random_state=2020,
        )
        train_data = np.concatenate((X, y[:, None]), axis=1)
        with open(pathlib.Path(data_filename), "w+") as data_file:
            writer = csv.writer(data_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D", "E", "true_class"])
            writer.writerows(train_data)
        # Features
        features = "-model-features A:float:1 B:float:1 C:float:1 D:float:1 E:float:1".split()

        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "vwmodel",
            *features,
            "-model-predict",
            "true_class:int:1",
            "-sources",
            "training_data=csv",
            "-source-filename",
            data_filename,
            "-model-vwcmd",
            "loss_function",
            "logistic",
            "l2",
            "0.04",
            "-model-convert_to_vw",
            "-model-use_binary_label",
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "vwmodel",
            *features,
            "-model-predict",
            "true_class:int:1",
            "-sources",
            "test_data=csv",
            "-source-filename",
            data_filename,
            "-model-vwcmd",
            "binary",
            "True",
            "-model-use_binary_label",
            "-model-convert_to_vw",
        )
        # Ensure JSON output works as expected (#261)
        with contextlib.redirect_stdout(self.stdout):
            # Make prediction
            await CLI._main(
                "predict",
                "all",
                "-model",
                "vwmodel",
                *features,
                "-model-predict",
                "true_class:int:1",
                "-sources",
                "predict_data=csv",
                "-source-filename",
                data_filename,
                "-model-vwcmd",
                "binary",
                "True",
                "-model-convert_to_vw",
                "-model-use_binary_label",
            )
        results = json.loads(self.stdout.getvalue())
        self.assertTrue(isinstance(results, list))
        self.assertTrue(results)
        results = results[0]
        self.assertIn("prediction", results)
        results = results["prediction"]
        self.assertIn("true_class", results)
        results = results["true_class"]
        self.assertIn("value", results)
        results = results["value"]
        self.assertIn(results, [1, -1])
