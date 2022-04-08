import pathlib
from typing import Type

import pandas as pd
from orion import Orion
from orion.data import load_signal

from dffml import (
    config,
    field,
    entrypoint,
    SimpleModel,
    ModelNotTrained,
    Accuracy,
    Feature,
    Features,
    SourcesContext,
    Record,
)


# Hyperparameters are passed in as tuples
def tup_to_dict(tup):
    tup = (tup,)
    dic = {}
    for param in tup:
        dic[param[0]] = param[1]
    return dic


@config
class OrionModelConfig:
    hyperparameters: tuple = field(
        "Hyperparameters for training the model",
        default=("keras.Sequential.LSTMTimeSeriesRegressor#1", {"epochs": 5}),
    )
    pipeline: str = field(
        "Orion pipeline to be used in model training",
        default="lstm_dynamic_threshold",
    )
    directory: pathlib.Path = field(
        "Filepath to save model configs", default="model"
    )


@entrypoint("orion")
class OrionModel(SimpleModel):
    r"""
    Time Series anomaly detection using Orion.

    The dataset used for these examples is generated through orion/tests/gen_data.py
    Run it with python ./tests/gen_data.py

    The same is also available in orion/examples/gen_data.py

    The data is passed in the format of a pandas table with 2 columns:
        1. timestamp: an INTEGER or FLOAT column with the time of the observation in Unix Time Format
        2. value: an INTEGER or FLOAT column with the observed value at the indicated timestamp

    **train.csv**

    .. code-block::
        :test:
        :filepath: train.csv

        File is generated through tests/gen_data.py

    The dataset used for testing

    **test.csv**

    .. code-block::
        :test:
        :filepath: test.csv

        File is generated through tests/gen_data.py

    Train the model

    .. code-block:: console
        :test:

        $ dffml train \
            -model orion \
            -model-hyperparameters "keras.Sequential.LSTMTimeSeriesRegressor#1"\,{\"epochs\": 5} \
            -sources f=csv \
            -source-filename ./tests/train.csv

    Assess the accuracy

    .. code-block:: console
        :test:

        $ dffml accuracy \
            -model orion \
            -model-hyperparameters "keras.Sequential.LSTMTimeSeriesRegressor#1"\,{\"epochs\": 5} \
            -sources pred=csv test=csv \
            -source-pred-filename ./tests/predict.csv \
            -source-test-filename ./tests/test.csv
        accuracy     0.950341
        f1           0.313208
        recall       0.185682
        precision    1.000000
        dtype: float64
        0.9503410641200546

    Make a prediction

    **predict.csv**

    .. code-block::
        :test:
        :filepath: predict.csv

        File is generated through tests/gen_data.py

    .. code-block:: console
        :test:

        $ dffml predict all \
                 -model orion \
                 -model-hyperparameters "keras.Sequential.LSTMTimeSeriesRegressor#1"\,{\"epochs\": 5} \
                 -sources f=csv \
                 -source-filename ./tests/predict.csv
        [
            {
                "extra": {},
                "features": {
                    "predict": {
                        "end": 1400198400,
                        "severity": 0.5252516607978518,
                        "start": 1398405600
                    }
                },
                "key": "predict"
            }
        ]

    Example usage of Time Series anomaly detection using Python

    **example_orion.py**

    .. literalinclude:: ../examples/example_orion.py
        :test:
        :filepath: example_orion.py

    .. code-block:: console
        :test:

        $ python example_orion.py
        accuracy     0.950341
        f1           0.313208
        recall       0.185682
        precision    1.000000
        dtype: float64
        Accuracy: 0.9503410641200546
    """
    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type = OrionModelConfig

    def __init__(self, config):
        super().__init__(config)
        # Checking to see if we train the model before testing
        self.trained = False

    async def train(self, sources: SourcesContext) -> None:
        # Loading the train data from a csv file that is included in our sources
        timestamp = []
        value = []
        async for record in sources.with_features(["timestamp", "value"]):
            timestamp.append(record.feature("timestamp"))
            value.append(record.feature("value"))

        train_data = pd.DataFrame({"timestamp": timestamp, "value": value})
        hyperparameters = tup_to_dict(self.config.hyperparameters)

        # Instantiating our model
        orion = Orion(
            pipeline=self.config.pipeline,
            hyperparameters=hyperparameters,
        )

        # Train model
        orion.fit(train_data)
        self.trained = True

        # Save model
        orion.save(self.config.directory / "orion_model.p")
        self.storage["trained"] = self.trained

    async def accuracy(self, sources: SourcesContext) -> Accuracy:
        # Ensure the model has been trained before we try to make a prediction
        self.trained = self.storage.get("trained", None)
        if self.trained is False:
            raise ModelNotTrained("Train model before assessing for accuracy")
        else:
            # Load our previously trained model from the pickle file
            orion = Orion.load(self.config.directory / "orion_model.p")

        # Loading the prediction data to make predictions that will later be compared with ground truth
        timestamp = []
        value = []
        async for record in sources.with_features(["timestamp", "value"]):
            timestamp.append(record.feature("timestamp"))
            value.append(record.feature("value"))

        new_data = pd.DataFrame({"timestamp": timestamp, "value": value})

        # Loading our ground truth values
        start = []
        end = []
        async for record in sources.with_features(["start", "end"]):
            start.append(record.feature("start"))
            end.append(record.feature("end"))

        ground_truth = pd.DataFrame({"start": start, "end": end})

        scores = orion.evaluate(new_data, ground_truth)
        print(scores)
        accuracy = scores.accuracy
        return Accuracy(accuracy)

    async def predict(self, sources: SourcesContext) -> pd.DataFrame:
        # Ensure the model has been trained before we try to make a prediction
        self.trained = self.storage.get("trained", None)
        if self.trained is False:
            raise ModelNotTrained("Train model before assessing for accuracy")
        else:
            # Load our previously trained model from the pickle file
            orion = Orion.load(self.config.directory / "orion_model.p")

        # Loading the prediction data to make predictions that will later be compared with ground truth
        timestamp = []
        value = []
        async for record in sources.with_features(["timestamp", "value"]):
            timestamp.append(record.feature("timestamp"))
            value.append(record.feature("value"))

        new_data = pd.DataFrame({"timestamp": timestamp, "value": value})

        anomalies = orion.detect(new_data)
        anomalies = anomalies.to_dict("records")
        self.storage["anomalies"] = anomalies

        for i in range(len(anomalies)):
            yield Record(
                "predict", data=dict(features=dict(predict=anomalies[i]))
            )
