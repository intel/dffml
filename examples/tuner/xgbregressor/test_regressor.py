import os
import random
import tempfile
import contextlib
import subprocess
import shutil

import numpy as np

from dffml.record import Record
from dffml.source.source import Sources
from dffml import tune, score, chdir
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature.feature import Feature, Features
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.accuracy import ClassificationAccuracy
from dffml.tuner.parameter_grid import ParameterGrid

from dffml_model_xgboost.xgbregressor import (
    XGBRegressorModel,
    XGBRegressorModelConfig,
)

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

def sh_filepath(filename):
    return os.path.join(os.path.dirname(__file__), filename)


@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(["bash", sh_filepath("../dataset_reg.sh")])
            shutil.copy(
                sh_filepath("xgbtest.json"), os.path.join(tempdir, "xgbtest.json"),
            )
            yield tempdir


class TestParameterGrid(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create an instance of the model
        cls.model =  XGBRegressorModel(
             XGBRegressorModelConfig(
                features=Features(
                    Feature("Feature1", float, 1), Feature("Feature2")
                ),
                predict=Feature("Target", float, 1),
                location=cls.model_dir.name,
            )
        )


        # Generating data f(x1,x2) = (2*x1 + 3*x2)//2
        _n_data = 2000
        _temp_data = np.random.rand(2, _n_data)
        cls.records = [
            Record(
                "x" + str(random.random()),
                data={
                    "features": {
                        "Feature1": float(_temp_data[0][i]),
                        "Feature2": float(_temp_data[1][i]),
                        "Target": (2 * _temp_data[0][i] + 3 * _temp_data[1][i]),
                    }
                },
            )
            for i in range(0, _n_data)
        ]

        cls.trainSource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[:1800]))
        )
        cls.testSource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[1800:]))
        )

        cls.scorer = ClassificationAccuracy()
        cls.tuner = ParameterGrid(
            parameters = {
                "learning_rate": [0.01, 0.05, 0.1],
                "n_estimators": [20, 100, 200],
                "max_depth": [3,5,8]

            },
            objective = "min"
        )

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory where the model was stored to cleanup
        cls.model_dir.cleanup()

    async def test_00_tune(self):
        # Train the model on the training data
        acc = await tune(self.model, self.tuner, self.scorer, Features(Feature("Target", int, 1)), self.trainSource, self.testSource)
        self.assertTrue(acc <= 10)
        acc = await score(self.model, self.scorer, Features(Feature("Target", int, 1)), self.testSource)
        self.assertTrue(acc <= 10)

    async def test_01_tune(self):
        # Tuning using CLI
        with directory_with_csv_files() as tempdir:
            stdout = subprocess.check_output(
                ["bash", sh_filepath("tune.sh")]
            )
            self.assertEqual(round(float(stdout.decode().strip())), 0)

