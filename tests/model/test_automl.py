import os
import random
import tempfile
import contextlib
import subprocess
import shutil


import numpy as np

from dffml.record import Record
from dffml.source.source import Sources
from dffml import train, score, chdir
from dffml.util.asynctestcase import AsyncTestCase
from dffml.feature.feature import Feature, Features
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.accuracy import ClassificationAccuracy
from dffml.tuner.parameter_grid import ParameterGrid
from dffml.model.automl import AutoMLModel

def sh_filepath(filename):
    return os.path.join(os.path.dirname(__file__), filename)

@contextlib.contextmanager
def directory_with_csv_files():
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            subprocess.check_output(["bash", sh_filepath("../dataset_cls.sh")])
            shutil.copy(
                sh_filepath("xgbtest.json"), os.path.join(tempdir, "xgbtest.json"),
            )
            yield tempdir

class TestAutoMLModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create an instance of the model

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
                        "Target": (2 * _temp_data[0][i] + 3 * _temp_data[1][i])
                        // 2,
                    }
                },
            )
            for i in range(0, _n_data)
        ]

        cls.trainingsource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[:1800]))
        )
        cls.testsource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[1800:]))
        )

        cls.scorer = ClassificationAccuracy()
        cls.tuner = ParameterGrid()
        cls.model = AutoMLModel(
            predict="Target",
            features=["Feature1", "Feature2"],
            location=cls.model_dir.name,
            tuner = cls.tuner,
            scorer = cls.scorer,
            models = ["xgbclassifier", "scikitsvc"],
            objective="max",
            parameters = {
                "xgbclassifier":  {
                    "learning_rate": [0.01, 0.05, 0.1],
                    "n_estimators": [20, 100, 200],
                     "max_depth": [3,5,8]
                },
                "scikitsvc": {
                    "gamma": [0.001, 0.1],
                    "C": [1, 10]
                }
            }

        )

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory where the model was stored to cleanup
        cls.model_dir.cleanup()


    async def test_00_train(self):
        await train(self.model, self.trainingsource)

    
    async def test_01_score(self):
        # Use the test data to assess the model's accuracy
        res = await score(
            self.model, self.scorer, Feature("Target", float, 1), self.testsource
        )
        # Ensure the accuracy is above 80%
        print(res)
        self.assertTrue(res > 0.8) 

    async def test_02_predict(self):
        # reduce overfitting
        res_train = await score(
            self.model,
            self.scorer,
            Feature("Target", float, 1),
            self.trainingsource,
        )

        res_test = await score(
            self.model,
            self.scorer,
            Feature("Target", float, 1),
            self.testsource,
        )
        # Test fails if the difference between training and testing is more that 5%
        self.assertLess(res_train - res_test, 0.05)
    
