import pathlib
from typing import AsyncIterator, Tuple, Any

import numpy as np

from dffml import (
    config,
    field,
    entrypoint,
    SimpleModel,
    ModelNotTrained,
    Accuracy,
    Feature,
    Features,
    Sources,
    Record,
)


@config
class LogisticRegressionConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on")
    directory: pathlib.Path = field(
        "Directory where state should be saved",
        default=pathlib.Path("~", ".cache", "dffml", "scratch"),
    )


@entrypoint("scratchlgrsag")
class LogisticRegression(SimpleModel):
    r"""
    Logistic Regression using stochastic average gradient descent optimizer


    .. code-block:: console

        $ cat > dataset.csv << EOF
        f1,ans
        0.1,0
        0.7,1
        0.6,1
        0.2,0
        0.8,1
        EOF
        $ dffml train \
            -model scratchlgrsag \
            -model-features f1:float:1 \
            -model-predict ans:int:1 \
            -sources f=csv \
            -source-filename dataset.csv \
            -log debug
        $ dffml accuracy \
            -model scratchlgrsag \
            -model-features f1:float:1 \
            -model-predict ans:int:1 \
            -sources f=csv \
            -source-filename dataset.csv \
            -log debug
        1.0
        $ echo -e 'f1,ans\n0.8,0\n' | \
          dffml predict all \
            -model scratchlgrsag \
            -model-features f1:float:1 \
            -model-predict ans:int:1 \
            -sources f=csv \
            -source-filename /dev/stdin \
            -log debug
        [
            {
                "extra": {},
                "features": {
                    "ans": 0,
                    "f1": 0.8
                },
                "last_updated": "2020-03-19T13:41:08Z",
                "prediction": {
                    "ans": {
                        "confidence": 1.0,
                        "value": 1
                    }
                },
                "key": "0"
            }
        ]

    """
    # The configuration class needs to be set as the CONFIG property
    CONFIG = LogisticRegressionConfig
    # Logistic Regression only supports training on a single feature
    NUM_SUPPORTED_FEATURES = 1
    # We only support single dimensional values, non-matrix / array
    SUPPORTED_LENGTHS = [1]

    def __init__(self, config):
        super().__init__(config)
        self.xData = np.array([])
        self.yData = np.array([])

    @property
    def separating_line(self):
        """
        Load separating_line from disk, if it hasn't been set yet, return None
        """
        return self.storage.get("separating_line", None)

    @separating_line.setter
    def separating_line(self, sline):
        """
        Set separating_line in self.storage so it will be saved to disk
        """
        self.storage["separating_line"] = sline

    def predict_input(self, x):
        """
        The Logistic regression with SAG optimizer: returns w * x + b > 0.5
        """
        prediction = self.separating_line[0] * x + self.separating_line[1]
        if prediction > 0.5:
            prediction = 1
        else:
            prediction = 0
        self.logger.debug(
            "Predicted Value of {} {}:".format(
                self.config.predict.NAME, prediction
            )
        )
        return prediction

    def best_separating_line(self):
        """
        Determine the best separating hyperplane (here, the integer weight) 
        s.t. w * x + b is well separable from 0.5.
        """
        self.logger.debug(
            "Number of input records: {}".format(len(self.xData))
        )
        x = self.xData  # feature array
        y = self.yData  # class array
        learning_rate = 0.01  # learning rate for step: weight -= lr * step
        w = 0.01  # initial weight
        b = 0.0  # here unbiased data is considered so b = 0
        # epochs' loop: 1500 epochs
        for _ in range(0, 1500):
            z = w * x + b
            val = -np.multiply(y, z)
            num = -np.multiply(y, np.exp(val))
            den = 1 + np.exp(val)
            f = num / den  # f is gradient dJ for each data point
            gradJ = np.sum(x * f)  # total dJ
            w = w - learning_rate * gradJ / len(x)  # SAG subtraction
        # Accuracy calculation
        error = 0  # incorrect values
        for x_id in range(len(x)):
            yhat = x[x_id] * w + b > 0.5
            if yhat:
                yhat = 1
            else:
                yhat = 0
            if yhat != y[x_id]:
                error += 1
        accuracy = 1 - (error / len(x))
        return (w, b, accuracy)

    async def train(self, sources: Sources):
        async for record in sources.with_features(
            self.features + [self.config.predict.NAME]
        ):
            feature_data = record.features(
                self.features + [self.config.predict.NAME]
            )
            self.xData = np.append(self.xData, feature_data[self.features[0]])
            self.yData = np.append(
                self.yData, feature_data[self.config.predict.NAME]
            )
        self.separating_line = self.best_separating_line()

    async def accuracy(self, sources: Sources) -> Accuracy:
        # Ensure the model has been trained before we try to make a prediction
        if self.separating_line is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")
        accuracy_value = self.separating_line[2]
        return Accuracy(accuracy_value)

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        # Ensure the model has been trained before we try to make a prediction
        if self.separating_line is None:
            raise ModelNotTrained("Train model before prediction.")
        target = self.config.predict.NAME
        async for record in records:
            feature_data = record.features(self.features)
            record.predicted(
                target,
                self.predict_input(feature_data[self.features[0]]),
                self.separating_line[2],
            )
            yield record
