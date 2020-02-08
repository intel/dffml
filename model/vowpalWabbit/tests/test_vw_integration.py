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

# TODO generate data on fly
class TestVWModel(IntegrationCLITestCase):
    async def test_run(self):
        self.required_plugins("dffml-model-vowpalWabbit")
        # Create the training data
        train_filename = self.mktempfile() + ".csv"
        pathlib.Path(train_filename).write_text(
            inspect.cleandoc(
                """
                Clump_Thickness,Uniformity_of_Cell_Size,Uniformity_of_Cell_Shape,Marginal_Adhesion,Single_Epithelial_Cell_Size,Bare_Nuclei,Bland_Chromatin,Normal_Nucleoli,Mitoses,Class
                3,4,5,2,6,8,4,1,1,-1
                1,1,1,1,3,2,2,1,1,1
                3,1,1,3,8,1,5,8,1,1
                8,8,7,4,10,10,7,8,7,-1
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
                1,1,1,1,1,1,3,1,1,1
                7,2,4,1,6,10,5,4,3,-1
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
                7,2,4,1,6,10,5,4,3
                3,1,1,3,8,1,5,8,1,1
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
            "vwmodel",
            *features,
            "-model-predict",
            "Class:int:1",
            "-sources",
            "training_data=csv",
            "-source-filename",
            train_filename,
            "-model-vwcmd",
            "vw --loss_function logistic --binary --l2 0.04",  # TODO Fix parsing issue to remove redundant `vw`
            "-model-convert_to_vw",
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "vwmodel",
            *features,
            "-model-predict",
            "Class:int:1",
            "-sources",
            "test_data=csv",
            "-source-filename",
            test_filename,
            "-model-vwcmd",
            "vw --loss_function logistic --link logistic --l2 0.04",
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
                "Class:int:1",
                "-sources",
                "predict_data=csv",
                "-source-filename",
                predict_filename,
                "-model-vwcmd",
                "vw --loss_function logistic --link logistic --l2 0.04",
                "-model-convert_to_vw",
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
        self.assertIn(results, [1, -1])
