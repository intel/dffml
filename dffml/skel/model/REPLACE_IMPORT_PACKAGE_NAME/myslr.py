import pathlib
import statistics
from typing import AsyncIterator, Type

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


def matrix_subtract(one, two):
    return [
        one_element - two_element for one_element, two_element in zip(one, two)
    ]


def matrix_multiply(one, two):
    return [
        one_element * two_element for one_element, two_element in zip(one, two)
    ]


def squared_error(y, line):
    return sum(map(lambda element: element ** 2, matrix_subtract(y, line)))


def coeff_of_deter(y, regression_line):
    y_mean_line = [statistics.mean(y)] * len(y)
    squared_error_mean = squared_error(y, y_mean_line)
    squared_error_regression = squared_error(y, regression_line)
    # Handle 1.0 accuracy case
    if squared_error_mean == 0:
        return 1.0
    return 1.0 - (squared_error_regression / squared_error_mean)


def best_fit_line(x, y):
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    m = (mean_x * mean_y - statistics.mean(matrix_multiply(x, y))) / (
        (mean_x ** 2) - statistics.mean(matrix_multiply(x, x))
    )
    b = mean_y - (m * mean_x)
    regression_line = [m * x_element + b for x_element in x]
    accuracy = coeff_of_deter(y, regression_line)
    return m, b, accuracy


@config
class MySLRModelConfig:
    features: Features = field(
        "Features to train on (myslr only supports one)"
    )
    predict: Feature = field("Label or the value to be predicted")
    directory: pathlib.Path = field("Directory where state should be saved")


@entrypoint("myslr")
class MySLRModel(SimpleModel):
    r"""
    Example Logistic Regression training one variable to predict another.

    The dataset used for training

    **train.csv**

    .. code-block::
        :test:
        :filepath: train.csv

        x,y
        0.0,0
        0.1,1
        0.2,2
        0.3,3
        0.4,4
        0.5,5

    The dataset used for testing

    **test.csv**

    .. code-block::
        :test:
        :filepath: test.csv

        x,y
        0.6,6
        0.7,7

    Train the model

    .. code-block:: console
        :test:

        $ dffml train \
            -model myslr \
            -model-features x:float:1 \
            -model-predict y:int:1 \
            -model-directory tempdir \
            -sources f=csv \
            -source-filename train.csv

    Assess the accuracy

    .. code-block:: console
        :test:

        $ dffml accuracy \
            -model myslr \
            -model-features x:float:1 \
            -model-predict y:int:1 \
            -model-directory tempdir \
            -sources f=csv \
            -source-filename test.csv
        1.0

    Make a prediction

    **predict.csv**

    .. code-block::
        :test:
        :filepath: predict.csv

        x
        0.8

    .. code-block:: console
        :test:

        $ dffml predict all \
            -model myslr \
            -model-features x:float:1 \
            -model-predict y:int:1 \
            -model-directory tempdir \
            -sources f=csv \
            -source-filename predict.csv
        [
            {
                "extra": {},
                "features": {
                    "x": 0.8
                },
                "key": "0",
                "last_updated": "2020-11-15T16:22:25Z",
                "prediction": {
                    "y": {
                        "confidence": 1.0,
                        "value": 7.999999999999998
                    }
                }
            }
        ]

    Example usage of Logistic Regression using Python

    **example_myslr.py**

    .. literalinclude:: ../examples/example_myslr.py
        :test:
        :filepath: example_myslr.py

    .. code-block:: console
        :test:

        $ python example_myslr.py
        Accuracy: 1.0
        {'x': 0.9, 'y': 4}
    """
    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type = MySLRModelConfig

    def __init__(self, config):
        super().__init__(config)
        # Simple linear regression only supports a single input feature
        if len(self.config.features) != 1:
            raise ValueError("Model only support a single feature")

    async def train(self, sources: SourcesContext) -> None:
        # X and Y data
        x = []
        y = []
        # Go through all records that have the feature we're training on and the
        # feature we want to predict.
        async for record in sources.with_features(
            [self.config.features[0].name, self.config.predict.name]
        ):
            x.append(record.feature(self.config.features[0].name))
            y.append(record.feature(self.config.predict.name))
        # Use self.logger to report how many records are being used for training
        self.logger.debug("Number of training records: %d", len(x))
        # Save m, b, and accuracy
        self.storage["regression_line"] = best_fit_line(x, y)

    async def accuracy(self, sources: SourcesContext) -> Accuracy:
        # Load saved regression line
        regression_line = self.storage.get("regression_line", None)
        # Ensure the model has been trained before we try to make a prediction
        if regression_line is None:
            raise ModelNotTrained("Train model before assessing for accuracy")
        # Split regression line tuple into variables, ignore accuracy from
        # training data since we'll be re-calculating it for the test data
        m, b, _accuracy = regression_line
        # X and Y data
        x = []
        y = []
        # Go through all records that have the feature we're testing on and the
        # feature we want to predict.
        async for record in sources.with_features(
            [self.config.features[0].name, self.config.predict.name]
        ):
            x.append(record.feature(self.config.features[0].name))
            y.append(record.feature(self.config.predict.name))
        # Use self.logger to report how many records are being used for testing
        self.logger.debug("Number of test records: %d", len(x))
        # Calculate the regression line for test data and accuracy of line
        regression_line = [m * x_element + b for x_element in x]
        accuracy = coeff_of_deter(y, regression_line)
        # Update the accuracy to be the accuracy when assessed on the test data
        self.storage["regression_line"] = m, b, accuracy
        return Accuracy(accuracy)

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:
        # Load saved regression line
        regression_line = self.storage.get("regression_line", None)
        # Ensure the model has been trained before we try to make a prediction
        if regression_line is None:
            raise ModelNotTrained("Train model before prediction")
        # Expand the regression_line into named variables
        m, b, accuracy = regression_line
        # Iterate through each record that needs a prediction
        async for record in sources.with_features(
            [self.config.features[0].name]
        ):
            # Grab the x data from the record
            x = record.feature(self.config.features[0].name)
            # Calculate y
            y = m * x + b
            # Set the calculated value with the estimated accuracy
            record.predicted(self.config.predict.name, y, accuracy)
            # Yield the record to the caller
            yield record
