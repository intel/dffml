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
from sklearn.datasets import make_blobs, make_regression

from dffml.cli.cli import CLI
from dffml.util.asynctestcase import IntegrationCLITestCase


class TestScikitClassification(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-scikit")
        # Create the training data
        train_filename = self.mktempfile() + ".csv"
        model_dir = self.mktempdir()
        train_data, y = make_blobs(
            n_samples=40, centers=2, n_features=4, random_state=200
        )
        train_data = np.concatenate((train_data, y[:, None]), axis=1)
        with open(pathlib.Path(train_filename), "w+") as train_file:
            writer = csv.writer(train_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D", "true_label"])
            writer.writerows(train_data)

        # Create the test data
        test_filename = self.mktempfile() + ".csv"
        test_data, y = make_blobs(
            n_samples=20, centers=2, n_features=4, random_state=200
        )
        test_data = np.concatenate((test_data, y[:, None]), axis=1)
        with open(pathlib.Path(test_filename), "w+") as test_file:
            writer = csv.writer(test_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D", "true_label"])
            writer.writerows(test_data)

        # Create the prediction data
        predict_filename = self.mktempfile() + ".csv"
        predict_data, y = make_blobs(
            n_samples=1, centers=2, n_features=4, random_state=200
        )
        with open(pathlib.Path(predict_filename), "w+") as predict_file:
            writer = csv.writer(predict_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D"])
            writer.writerows(predict_data)

        # Features
        features = (
            "-model-features A:float:1 B:float:1 C:float:1 D:float:1".split()
        )
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "scikitsvc",
            *features,
            "-model-predict",
            "true_label:int:1",
            "-model-directory",
            model_dir,
            "-sources",
            "training_data=csv",
            "-source-filename",
            train_filename,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "scikitsvc",
            *features,
            "-model-predict",
            "true_label:int:1",
            "-model-directory",
            model_dir,
            "-sources",
            "test_data=csv",
            "-source-filename",
            test_filename,
        )
        # Ensure JSON output works as expected (#261)
        with contextlib.redirect_stdout(self.stdout):
            # Make prediction
            await CLI._main(
                "predict",
                "all",
                "-model",
                "scikitsvc",
                *features,
                "-model-predict",
                "true_label:int:1",
                "-model-directory",
                model_dir,
                "-sources",
                "predict_data=csv",
                "-source-filename",
                predict_filename,
            )
        results = json.loads(self.stdout.getvalue())
        self.assertTrue(isinstance(results, list))
        self.assertTrue(results)
        results = results[0]
        self.assertIn("prediction", results)
        results = results["prediction"]
        self.assertIn("true_label", results)
        results = results["true_label"]
        self.assertIn("value", results)
        results = results["value"]
        self.assertEqual(y.item(), results)


class TestScikitRegression(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-scikit")
        # Create the training data
        train_filename = self.mktempfile() + ".csv"
        train_data, y = make_regression(
            n_samples=40, n_features=4, noise=0.1, random_state=200
        )
        train_data = np.concatenate((train_data, y[:, None]), axis=1)
        with open(pathlib.Path(train_filename), "w+") as train_file:
            writer = csv.writer(train_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D", "true_label"])
            writer.writerows(train_data)

        # Create the test data
        test_filename = self.mktempfile() + ".csv"
        test_data, y = make_regression(
            n_samples=10, n_features=4, noise=0.1, random_state=200
        )
        test_data = np.concatenate((test_data, y[:, None]), axis=1)
        with open(pathlib.Path(test_filename), "w+") as test_file:
            writer = csv.writer(test_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D", "true_label"])
            writer.writerows(test_data)

        # Create the prediction data
        predict_filename = self.mktempfile() + ".csv"
        predict_data, y = make_regression(
            n_samples=1, n_features=4, noise=0, random_state=200
        )
        with open(pathlib.Path(predict_filename), "w+") as predict_file:
            writer = csv.writer(predict_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D"])
            writer.writerows(predict_data)

        # Features
        features = (
            "-model-features A:float:1 B:float:1 C:float:1 D:float:1".split()
        )
        model_dir = self.mktempdir()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "scikitridge",
            *features,
            "-model-predict",
            "true_label:float:1",
            "-model-directory",
            model_dir,
            "-sources",
            "training_data=csv",
            "-source-filename",
            train_filename,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "scikitridge",
            *features,
            "-model-predict",
            "true_label:float:1",
            "-model-directory",
            model_dir,
            "-sources",
            "test_data=csv",
            "-source-filename",
            test_filename,
        )
        # Ensure JSON output works as expected (#261)
        with contextlib.redirect_stdout(self.stdout):
            # Make prediction
            await CLI._main(
                "predict",
                "all",
                "-model",
                "scikitridge",
                *features,
                "-model-predict",
                "true_label:float:1",
                "-model-directory",
                model_dir,
                "-sources",
                "predict_data=csv",
                "-source-filename",
                predict_filename,
            )
        results = json.loads(self.stdout.getvalue())
        self.assertTrue(isinstance(results, list))
        self.assertTrue(results)
        results = results[0]
        self.assertIn("prediction", results)
        results = results["prediction"]
        self.assertIn("true_label", results)
        results = results["true_label"]
        self.assertIn("value", results)
        results = results["value"]
        self.assertTrue(results is not None)


class TestScikitClustering(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-scikit")
        # Create the training data
        """ train_data = [[ 7.67983358, -3.43833087,  0.70319017, -4.00173485],
                         [ 8.68078273, -3.79913846,  2.86810681,  7.13800644],
                         ...]"""
        train_filename = self.mktempfile() + ".csv"
        train_data, y = make_blobs(
            n_samples=40, centers=4, n_features=4, random_state=2020
        )
        train_data = np.concatenate((train_data, y[:, None]), axis=1)
        with open(pathlib.Path(train_filename), "w+") as train_file:
            writer = csv.writer(train_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D", "true_label"])
            writer.writerows(train_data)

        # Create the test data
        test_filename = self.mktempfile() + ".csv"
        test_data, y = make_blobs(
            n_samples=20, centers=4, n_features=4, random_state=2019
        )
        test_data = np.concatenate((test_data, y[:, None]), axis=1)
        with open(pathlib.Path(test_filename), "w+") as test_file:
            writer = csv.writer(test_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D", "true_label"])
            writer.writerows(test_data)

        # Create the prediction data
        predict_filename = self.mktempfile() + ".csv"
        predict_data, y = make_blobs(
            n_samples=10, centers=4, n_features=4, random_state=2021
        )
        with open(pathlib.Path(predict_filename), "w+") as predict_file:
            writer = csv.writer(predict_file, delimiter=",")
            writer.writerow(["A", "B", "C", "D"])
            writer.writerows(predict_data)

        # Features
        features = (
            "-model-features A:float:1 B:float:1 C:float:1 D:float:1".split()
        )
        model_dir = self.mktempdir()
        # ind_w_labl --> inductive model with true cluster label
        # ind_wo_labl --> inductive model without true cluster label
        # tran_w_labl --> transductive model with true cluster label
        # tran_wo_labl --> transductive model without true cluster label
        for algo in [
            "ind_w_labl",
            "ind_wo_labl",
            "tran_w_labl",
            "tran_wo_labl",
        ]:
            if algo is "ind_w_labl":
                model, true_clstr, train_file, test_file, predict_file = (
                    "scikitkmeans",
                    "true_label:int:1",
                    train_filename,
                    test_filename,
                    predict_filename,
                )
            elif algo is "ind_wo_labl":
                model, true_clstr, train_file, test_file, predict_file = (
                    "scikitap",
                    None,
                    train_filename,
                    test_filename,
                    predict_filename,
                )
            elif algo is "tran_w_labl":
                model, true_clstr, train_file, test_file, predict_file = (
                    "scikitoptics",
                    "true_label:int:1",
                    train_filename,
                    train_filename,
                    train_filename,
                )
            elif algo is "tran_wo_labl":
                model, true_clstr, train_file, test_file, predict_file = (
                    "scikitac",
                    None,
                    train_filename,
                    train_filename,
                    train_filename,
                )
            # Train the model
            await CLI.cli(
                "train",
                "-model",
                model,
                *features,
                "-model-directory",
                model_dir,
                "-sources",
                "training_data=csv",
                "-source-filename",
                train_file,
            )
            # Assess accuracy
            await CLI.cli(
                *(
                    [
                        "accuracy",
                        "-model",
                        model,
                        *features,
                        "-model-directory",
                        model_dir,
                        "-sources",
                        "test_data=csv",
                        "-source-filename",
                        test_file,
                    ]
                    + (
                        ["-model-tcluster", true_clstr]
                        if true_clstr is not None
                        else []
                    )
                )
            )
            with contextlib.redirect_stdout(self.stdout):
                # Make prediction
                await CLI._main(
                    "predict",
                    "all",
                    "-model",
                    model,
                    "-model-directory",
                    model_dir,
                    *features,
                    "-sources",
                    "predict_data=csv",
                    "-source-filename",
                    predict_file,
                )
            results = json.loads(self.stdout.getvalue())
            self.stdout.truncate(0)
            self.stdout.seek(0)
            self.assertTrue(isinstance(results, list))
            self.assertTrue(results)
            results = results[0]
            self.assertIn("prediction", results)
            results = results["prediction"]
            self.assertIn("cluster", results)
            results = results["cluster"]
            self.assertIn("value", results)
            results = results["value"]
            self.assertTrue(results is not None)
