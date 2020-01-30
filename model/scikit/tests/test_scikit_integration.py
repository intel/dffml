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

from dffml.cli.cli import CLI
from dffml.util.asynctestcase import IntegrationCLITestCase


from sklearn.datasets import make_blobs


class TestScikitClassification(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-scikit")
        # Create the training data
        train_filename = self.mktempfile() + ".csv"
        pathlib.Path(train_filename).write_text(
            inspect.cleandoc(
                """
                Clump_Thickness,Uniformity_of_Cell_Size,Uniformity_of_Cell_Shape,Marginal_Adhesion,Single_Epithelial_Cell_Size,Bare_Nuclei,Bland_Chromatin,Normal_Nucleoli,Mitoses,Class
                3,4,5,2,6,8,4,1,1,4
                1,1,1,1,3,2,2,1,1,2
                3,1,1,3,8,1,5,8,1,2
                8,8,7,4,10,10,7,8,7,4
                """
            )
            + "\n"
        )
        # Create the test data
        test_filename = self.mktempfile() + ".csv"
        pathlib.Path(test_filename).write_text(
            inspect.cleandoc(
                """
                Clump_Thickness,Uniformity_of_Cell_Size,Uniformity_of_Cell_Shape,Marginal_Adhesion,Single_Epithelial_Cell_Size,Bare_Nuclei,Bland_Chromatin,Normal_Nucleoli,Mitoses,Class
                1,1,1,1,1,1,3,1,1,2
                7,2,4,1,6,10,5,4,3,4
                """
            )
            + "\n"
        )
        # Create the prediction data
        predict_filename = self.mktempfile() + ".csv"
        pathlib.Path(predict_filename).write_text(
            inspect.cleandoc(
                """
                Clump_Thickness,Uniformity_of_Cell_Size,Uniformity_of_Cell_Shape,Marginal_Adhesion,Single_Epithelial_Cell_Size,Bare_Nuclei,Bland_Chromatin,Normal_Nucleoli,Mitoses,Class
                5,3,3,3,6,10,3,1,1
                """
            )
            + "\n"
        )
        # Features
        features = "-model-features Clump_Thickness:int:1 Uniformity_of_Cell_Size:int:1 Uniformity_of_Cell_Shape:int:1 Marginal_Adhesion:int:1 Single_Epithelial_Cell_Size:int:1 Bare_Nuclei:int:1 Bland_Chromatin:int:1 Normal_Nucleoli:int:1 Mitoses:int:1".split()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "scikitsvc",
            *features,
            "-model-predict",
            "Class:int:1",
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
            "Class:int:1",
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
                "Class:int:1",
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
        self.assertIn("Class", results)
        results = results["Class"]
        self.assertIn("value", results)
        results = results["value"]
        self.assertEqual(4, results)


class TestScikitRegression(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-scikit")
        # Create the training data
        train_filename = self.mktempfile() + ".csv"
        pathlib.Path(train_filename).write_text(
            inspect.cleandoc(
                """
                crim,zn,indus,chas,nox,rm,age,dis,rad,tax,ptratio,b,lstat,medv
                0.00632,18,2.31,0,0.538,6.575,65.2,4.09,1,296,15.3,396.9,4.98,24
                0.02731,0,7.07,0,0.469,6.421,78.9,4.9671,2,242,17.8,396.9,9.14,21.6
                0.02729,0,7.07,0,0.469,7.185,61.1,4.9671,2,242,17.8,392.83,4.03,34.7
                0.03237,0,2.18,0,0.458,6.998,45.8,6.0622,3,222,18.7,394.63,2.94,33.4
                0.06905,0,2.18,0,0.458,7.147,54.2,6.0622,3,222,18.7,396.9,5.33,36.2
                """
            )
            + "\n"
        )
        # Create the test data
        test_filename = self.mktempfile() + ".csv"
        pathlib.Path(test_filename).write_text(
            inspect.cleandoc(
                """
                crim,zn,indus,chas,nox,rm,age,dis,rad,tax,ptratio,b,lstat,medv
                0.02985,0,2.18,0,0.458,6.43,58.7,6.0622,3,222,18.7,394.12,5.21,28.7
                0.08829,12.5,7.87,0,0.524,6.012,66.6,5.5605,5,311,15.2,395.6,12.43,22.9
                """
            )
            + "\n"
        )
        # Create the prediction data
        predict_filename = self.mktempfile() + ".csv"
        pathlib.Path(predict_filename).write_text(
            inspect.cleandoc(
                """
                crim,zn,indus,chas,nox,rm,age,dis,rad,tax,ptratio,b,lstat,medv
                0.14455,12.5,7.87,0,0.524,6.172,96.1,5.9505,5,311,15.2,396.9,19.15,27.1
                """
            )
            + "\n"
        )
        # Features
        features = "-model-features crim:float:1 zn:float:1 indus:float:1 chas:int:1 nox:float:1 rm:float:1 age:int:1 dis:float:1 rad:int:1 tax:float:1 ptratio:float:1 b:float:1 lstat:float:1".split()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "scikitridge",
            *features,
            "-model-predict",
            "medv:float:1",
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
            "medv:float:1",
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
                "medv:float:1",
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
        self.assertIn("medv", results)
        results = results["medv"]
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
                "-sources",
                "training_data=csv",
                "-source-filename",
                train_file,
                "-source-readonly",
            )
            # Assess accuracy
            await CLI.cli(
                *(
                    [
                        "accuracy",
                        "-model",
                        model,
                        *features,
                        "-sources",
                        "test_data=csv",
                        "-source-readonly",
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
                    *features,
                    "-sources",
                    "predict_data=csv",
                    "-source-readonly",
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
            self.assertIn("Prediction", results)
            results = results["Prediction"]
            self.assertIn("value", results)
            results = results["value"]
            self.assertTrue(results is not None)
