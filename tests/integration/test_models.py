"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import re
import os
import io
import json
import inspect
import pathlib
import asyncio
import contextlib
import unittest.mock
from typing import Dict, Any

from dffml.repo import Repo
from dffml.base import config
from dffml.df.types import Definition, Operation, DataFlow, Input
from dffml.df.base import op
from dffml.cli.cli import CLI
from dffml.model.model import Model
from dffml.service.dev import Develop
from dffml.util.packaging import is_develop
from dffml.util.entrypoint import load
from dffml.config.config import BaseConfigLoader
from dffml.util.asynctestcase import AsyncTestCase

from .common import IntegrationCLITestCase


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
        features = "-model-features def:Clump_Thickness:int:1 def:Uniformity_of_Cell_Size:int:1 def:Uniformity_of_Cell_Shape:int:1 def:Marginal_Adhesion:int:1 def:Single_Epithelial_Cell_Size:int:1 def:Bare_Nuclei:int:1 def:Bland_Chromatin:int:1 def:Normal_Nucleoli:int:1 def:Mitoses:int:1".split()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "scikitsvc",
            *features,
            "-model-predict",
            "Class",
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
            "Class",
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
                "Class",
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
        self.assertIn("value", results)
        results = results["value"]
        self.assertEqual(4, results)
