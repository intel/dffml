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


class TestCSV(IntegrationCLITestCase):
    async def test_string_src_urls(self):
        # Test for issue #207
        self.required_plugins("dffml-model-scikit")
        # Create the training data
        train_filename = self.mktempfile(
            suffix=".csv",
            text="""
                Years,Expertise,Trust,Salary
                0,1,0.2,10
                1,3,0.4,20
                2,5,0.6,30
                3,7,0.8,40
                """,
        )
        # Create the test data
        test_filename = self.mktempfile(
            suffix=".csv",
            text="""
                Years,Expertise,Trust,Salary
                4,9,1.0,50
                5,11,1.2,60
                """,
        )
        # Create the prediction data
        predict_filename = self.mktempfile(
            suffix=".csv",
            text="""
                Years,Expertise,Trust
                6,13,1.4
                """,
        )
        # Features
        features = "-model-features def:Years:int:1 def:Expertise:int:1 def:Trust:float:1".split()
        # Train the model
        await CLI.cli(
            "train",
            "-model",
            "scikitlr",
            *features,
            "-model-predict",
            "Salary",
            "-sources",
            "training_data=csv",
            "-source-filename",
            train_filename,
        )
        # Assess accuracy
        await CLI.cli(
            "accuracy",
            "-model",
            "scikitlr",
            *features,
            "-model-predict",
            "Salary",
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
                "scikitlr",
                *features,
                "-model-predict",
                "Salary",
                "-sources",
                "predict_data=csv",
                "-source-filename",
                predict_filename,
            )
        results = json.loads(self.stdout.getvalue())
        self.assertTrue(isinstance(results, list))
        self.assertTrue(results)
        results = results[0]
        self.assertIn("src_url", results)
        self.assertEqual("0", results["src_url"])
        self.assertIn("prediction", results)
        self.assertIn("value", results["prediction"])
        self.assertEqual(70.0, results["prediction"]["value"])
