import pathlib
import statistics
from typing import AsyncIterator, Tuple, Any, Type, List

from ..base import config, field
from ..util.entrypoint import entrypoint
from .model import SimpleModel, ModelNotTrained
from .accuracy import Accuracy
from ..feature.feature import Feature, Features
from ..source.source import Sources, SourcesContext
from ..record import Record


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
class SLRModelConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on. For SLR only 1 allowed")
    directory: pathlib.Path = field("Directory where state should be saved")


@entrypoint("slr")
class SLRModel(SimpleModel):
    r"""
    Logistic Regression training one variable to predict another.

    The dataset used for training

    .. literalinclude:: /../examples/model/slr/dataset.sh

    Train the model

    .. literalinclude:: /../examples/model/slr/train.sh

    Assess the accuracy

    .. literalinclude:: /../examples/model/slr/accuracy.sh

    Output

    .. code-block:: console

        1.0

    Make a prediction

    .. literalinclude:: /../examples/model/slr/predict.sh

    Output

    .. code-block:: console

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

    Example usage of Logistic Regression using Python

    .. literalinclude:: /../examples/model/slr/slr.py

    """
    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type[SLRModelConfig] = SLRModelConfig
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
            self.features + [self.config.predict.name]
        ):
            x.append(record.feature(self.features[0]))
            y.append(record.feature(self.config.predict.name))
        # Use self.logger to report how many records are being used for training
        self.logger.debug("Number of input records: %d", len(x))
        # Save m, b, and accuracy
        self.storage["regression_line"] = best_fit_line(x, y)

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        # Load saved regression line
        regression_line = self.storage.get("regression_line", None)
        # Ensure the model has been trained before we try to make a prediction
        if regression_line is None:
            raise ModelNotTrained("Train model before prediction.")
        # Expand the regression_line into named variables
        m, b, accuracy = regression_line
        # Iterate through each record that needs a prediction
        async for record in sources.with_features(
            self.parent.config.features.names()
        ):
            # Grab the x data from the record
            x = record.feature(self.features[0])
            # Calculate y
            y = m * x + b
            # Set the calculated value with the estimated accuracy
            record.predicted(self.config.predict.name, y, accuracy)
            # Yield the record to the caller
            yield record
