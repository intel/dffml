import pathlib
import statistics
from typing import AsyncIterator, Tuple, Any, Type, List

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
    return (m, b, accuracy)


@config
class MiscModelConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on. For SLR only 1 allowed")
    directory: pathlib.Path = field(
        "Directory where state should be saved",
        default=pathlib.Path("~", ".cache", "dffml", "misc"),
    )


@entrypoint("misc")
class MiscModel(SimpleModel):
    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type[MiscModelConfig] = MiscModelConfig
    # Simple Linear Regression only supports training on a single feature.
    # Do not define NUM_SUPPORTED_FEATURES if you support arbitrary numbers of
    # features.
    NUM_SUPPORTED_FEATURES: int = 1
    # We only support single dimensional values, non-matrix / array
    # Do not define SUPPORTED_LENGTHS if you support arbitrary dimensions
    SUPPORTED_LENGTHS: List[int] = [1]

    async def train(self, sources: Sources) -> None:
        # X and Y data
        x = []
        y = []
        # Go through all records that have the feature we're training on and the
        # feature we want to predict. Since our model only supports 1 feature,
        # the self.features list will only have one element at index 0.
        async for record in sources.with_features(
            self.features + [self.config.predict.NAME]
        ):
            x.append(record.feature(self.features[0]))
            y.append(record.feature(self.config.predict.NAME))
        # Use self.logger to report how many records are being used for training
        self.logger.debug("Number of input records: %d", len(x))
        # Save m, b, and accuracy
        self.storage["regression_line"] = best_fit_line(x, y)

    async def accuracy(self, sources: Sources) -> Accuracy:
        # Load saved regression line
        regression_line = self.storage.get("regression_line", None)
        # Ensure the model has been trained before we try to make a prediction
        if regression_line is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")
        # Accuracy is the last element in regression_line, which is a list of
        # three values: m, b, and accuracy.
        return Accuracy(regression_line[2])

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        # Load saved regression line
        regression_line = self.storage.get("regression_line", None)
        # Ensure the model has been trained before we try to make a prediction
        if regression_line is None:
            raise ModelNotTrained("Train model before prediction.")
        # Expand the regression_line into named variables
        m, b, accuracy = regression_line
        # Iterate through each record that needs a prediction
        async for record in records:
            # Grab the x data from the record
            x = record.feature(self.features[0])
            # Calculate y
            y = m * x + b
            # Set the calculated value with the estimated accuracy
            record.predicted(self.config.predict.NAME, y, accuracy)
            # Yield the record to the caller
            yield record
