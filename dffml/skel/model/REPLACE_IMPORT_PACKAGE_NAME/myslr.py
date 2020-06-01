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
    Sources,
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
    return 1 - (squared_error_regression / squared_error_mean)


def best_fit_line(x, y):
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    m = (mean_x * mean_y - statistics.mean(matrix_multiply(x, y))) / (
        (mean_x ** 2) - statistics.mean(matrix_multiply(x, x))
    )
    b = mean_y - (m * mean_x)
    regression_line = [m * x + b for x in x]
    accuracy = coeff_of_deter(y, regression_line)
    return m, b, accuracy


@config
class MySLRModelConfig:
    feature: Feature = field("Feature to train on")
    predict: Feature = field("Label or the value to be predicted")
    directory: pathlib.Path = field("Directory where state should be saved")


@entrypoint("myslr")
class MySLRModel(SimpleModel):
    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type = MySLRModelConfig

    async def train(self, sources: Sources) -> None:
        # X and Y data
        x = []
        y = []
        # Go through all records that have the feature we're training on and the
        # feature we want to predict.
        async for record in sources.with_features(
            [self.config.feature.name, self.config.predict.name]
        ):
            x.append(record.feature(self.config.feature.name))
            y.append(record.feature(self.config.predict.name))
        # Use self.logger to report how many records are being used for training
        self.logger.debug("Number of training records: %d", len(x))
        # Save m, b, and accuracy
        self.storage["regression_line"] = best_fit_line(x, y)

    async def accuracy(self, sources: Sources) -> Accuracy:
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
            [self.config.feature.name, self.config.predict.name]
        ):
            x.append(record.feature(self.config.feature.name))
            y.append(record.feature(self.config.predict.name))
        # Use self.logger to report how many records are being used for testing
        self.logger.debug("Number of test records: %d", len(x))
        # Calculate the regression line for test data and accuracy of line
        regression_line = [m * x + b for x in x]
        accuracy = coeff_of_deter(y, regression_line)
        # Update the accuracy to be the accuracy when assessed on the test data
        self.storage["regression_line"] = m, b, accuracy
        return Accuracy(accuracy)

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Record]:
        # Load saved regression line
        regression_line = self.storage.get("regression_line", None)
        # Ensure the model has been trained before we try to make a prediction
        if regression_line is None:
            raise ModelNotTrained("Train model before prediction")
        # Expand the regression_line into named variables
        m, b, accuracy = regression_line
        # Iterate through each record that needs a prediction
        async for record in records:
            # Grab the x data from the record
            x = record.feature(self.config.feature.name)
            # Calculate y
            y = m * x + b
            # Set the calculated value with the estimated accuracy
            record.predicted(self.config.predict.name, y, accuracy)
            # Yield the record to the caller
            yield record
