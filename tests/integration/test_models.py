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
        features = "-model-features def:crim:float:1 def:zn:float:1 def:indus:float:1 def:chas:int:1 def:nox:float:1 def:rm:float:1 def:age:int:1 def:dis:float:1 def:rad:int:1 def:tax:float:1 def:ptratio:float:1 def:b:float:1 def:lstat:float:1".split()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "scikitridge",
            *features,
            "-model-predict",
            "medv",
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
            "medv",
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
                "medv",
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
        self.assertTrue(results is not None)
