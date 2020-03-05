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
class SLRConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on")
    directory: pathlib.Path = field(
        "Directory where state should be saved",
        default=pathlib.Path("~", ".cache", "dffml", "scratch"),
    )


@entrypoint("scratchslr")
class SLR(SimpleModel):
    r"""
    Simple Linear Regression Model for 2 variables implemented from scratch.
    Models are saved under the ``directory`` in subdirectories named after the
    hash of their feature names.

    .. code-block:: console

        $ cat > dataset.csv << EOF
        Years,Salary
        1,40
        2,50
        3,60
        4,70
        5,80
        EOF
        $ dffml train \
            -model scratchslr \
            -model-features Years:int:1 \
            -model-predict Salary:float:1 \
            -sources f=csv \
            -source-filename dataset.csv \
            -log debug
        $ dffml accuracy \
            -model scratchslr \
            -model-features Years:int:1 \
            -model-predict Salary:float:1 \
            -sources f=csv \
            -source-filename dataset.csv \
            -log debug
        1.0
        $ echo -e 'Years,Salary\n6,0\n' | \
          dffml predict all \
            -model scratchslr \
            -model-features Years:int:1 \
            -model-predict Salary:float:1 \
            -sources f=csv \
            -source-filename /dev/stdin \
            -log debug
        [
            {
                "extra": {},
                "features": {
                    "Salary": 0,
                    "Years": 6
                },
                "last_updated": "2019-07-19T09:46:45Z",
                "prediction": {
                    "Salary": {
                        "confidence": 1.0,
                        "value": 90.0
                    }
                },
                "key": "0"
            }
        ]

    """

    # The configuration class needs to be set as the CONFIG property
    CONFIG = SLRConfig
    # Simple Linear Regression only supports training on a single feature
    NUM_SUPPORTED_FEATURES = 1
    # We only support single dimensional values, non-matrix / array
    SUPPORTED_LENGTHS = [1]

    def __init__(self, config):
        super().__init__(config)
        self.xData = np.array([])
        self.yData = np.array([])

    @property
    def regression_line(self):
        """
        Load regression_line from disk, if it hasn't been set yet, return None
        """
        return self.storage.get("regression_line", None)

    @regression_line.setter
    def regression_line(self, rline):
        """
        Set regression_line in self.storage so it will be saved to disk
        """
        self.storage["regression_line"] = rline

    def predict_input(self, x):
        """
        Use the regression line to make a prediction by returning ``m * x + b``.
        """
        prediction = self.regression_line[0] * x + self.regression_line[1]
        self.logger.debug(
            "Predicted Value of {} {}:".format(
                self.config.predict.NAME, prediction
            )
        )
        return prediction

    def squared_error(self, ys, yline):
        return sum((ys - yline) ** 2)

    def coeff_of_deter(self, ys, regression_line):
        y_mean_line = [np.mean(ys) for y in ys]
        squared_error_mean = self.squared_error(ys, y_mean_line)
        squared_error_regression = self.squared_error(ys, regression_line)
        return 1 - (squared_error_regression / squared_error_mean)

    def best_fit_line(self):
        self.logger.debug(
            "Number of input records: {}".format(len(self.xData))
        )
        x = self.xData
        y = self.yData
        mean_x = np.mean(self.xData)
        mean_y = np.mean(self.yData)
        m = (mean_x * mean_y - np.mean(x * y)) / (
            (mean_x ** 2) - np.mean(x * x)
        )
        b = mean_y - (m * mean_x)
        regression_line = [m * x + b for x in x]
        accuracy = self.coeff_of_deter(y, regression_line)
        return (m, b, accuracy)

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
        self.regression_line = self.best_fit_line()

    async def accuracy(self, sources: Sources) -> Accuracy:
        # Ensure the model has been trained before we try to make a prediction
        if self.regression_line is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")
        accuracy_value = self.regression_line[2]
        return Accuracy(accuracy_value)

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        # Ensure the model has been trained before we try to make a prediction
        if self.regression_line is None:
            raise ModelNotTrained("Train model before prediction.")
        target = self.config.predict.NAME
        async for record in records:
            feature_data = record.features(self.features)
            record.predicted(
                target,
                self.predict_input(feature_data[self.features[0]]),
                self.regression_line[2],
            )
            yield record
