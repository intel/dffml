import random
import pathlib
import tempfile

import numpy as np

from dffml.record import Record
from dffml.base import config, field
from dffml.source.source import Sources
from dffml.model.accuracy import Accuracy
from dffml.util.entrypoint import entrypoint
from dffml.feature.feature import Feature, Features
from dffml.model.model import SimpleModel, ModelNotTrained
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml import (
    AsyncTestCase,
    Feature,
    Features,
    accuracy,
    predict,
    train,
    run_consoletest,
)

from dffml_model_scratch.anomalydetection import AnomalyModel


class TestAnomalyModel(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the trained model
        cls.model_dir = tempfile.TemporaryDirectory()
        # Create an instance of the model
        cls.model = AnomalyModel(
            features=Features(Feature("A", int, 1), Feature("B", int, 2),),
            predict=Feature("Y", int, 1),
            directory=cls.model_dir.name,
        )

        # Generating data

        _n_data = 1800
        _temp_data = np.random.normal(2, 1, size=(2, _n_data))
        cls.records = [
            Record(
                "x" + str(random.random()),
                data={
                    "features": {
                        "A": float(_temp_data[0][i]),
                        "B": float(_temp_data[1][i]),
                        "Y": (_temp_data[0][i] > 1 - _temp_data[1][i]).astype(
                            int
                        ),
                    }
                },
            )
            for i in range(0, _n_data)
        ]

        cls.trainingsource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[:1400]))
        )
        cls.testsource = Sources(
            MemorySource(MemorySourceConfig(records=cls.records[1400:]))
        )

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory where the model was stored to cleanup
        cls.model_dir.cleanup()

    async def test_00_train(self):
        # Train the model on the training data
        await train(self.model, self.trainingsource)

    async def test_01_accuracy(self):
        # Use the test data to assess the model's accuracy
        res = await accuracy(self.model, self.testsource)
        # Ensure the accuracy is above 80%
        self.assertTrue(0.8 <= res < 1.0)

    async def test_02_predict(self):
        right_prediction = 0
        wrong_prediction = 0
        # Get the prediction for each piece of test data
        async for i, features, prediction in predict(
            self.model, self.testsource
        ):
            # Grab the correct value
            correct = features["Y"]
            # Grab the predicted value
            prediction = prediction["Y"]["value"]
            if prediction == correct:
                right_prediction += 1
            else:
                wrong_prediction += 1
        # Check that more than 80% of the predictions are correct
        acceptable = 0.8
        self.assertGreater(
            right_prediction,
            (right_prediction + wrong_prediction) * (acceptable),
        )

    async def test_docstring(self):
        await run_consoletest(
            AnomalyModel,
            docs_root_dir=pathlib.Path(__file__).parents[3] / "docs",
        )
