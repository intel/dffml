import pathlib
from typing import AsyncIterator

import joblib
import numpy as np
import pandas as pd
from dffml import make_config_numpy
from dffml.base import config, field
from dffml.feature.feature import Feature, Features
from dffml.model.accuracy import Accuracy
from dffml.model.model import ModelNotTrained, SimpleModel
from dffml.record import Record
from dffml.source.source import Sources
from dffml.util.entrypoint import entrypoint
from sklearn.metrics import mean_squared_error

import lightgbm
from lightgbm import LGBMRegressor

# Configuration of LGBMRegressor
LGBMRegressorModelConfig = make_config_numpy(
    "LGBMClassifierModelConfig",
    lightgbm.LGBMModel.__init__,
    properties={
        "features": (Features, field("Features to train on")),
        "predict": (Feature, field("Label or the value to be predicted")),
        "directory": (
            pathlib.Path,
            field("Directory where state should be saved",),
        ),
    },
)


@entrypoint("lgbmregressor")
class LGBMRegressorModel(SimpleModel):
    r"""
    LightGBM (Light Gradient Boosting Machine) is a free and open source
    distributed gradient boosting framework for machine learning originally
    developed by Microsoft.

    It is much faster to train and based on decision tree algorithms and used
    for ranking, classification and other machine learning tasks.

    This model is used for regression problems.

    Examples
    --------

    Command line usage

    Download the training and testing date sets, change the headers to DFFML format.

    .. code-block::
        :test:

        $ wget http://download.tensorflow.org/data/iris_training.csv
        $ wget http://download.tensorflow.org/data/iris_test.csv
        $ sed -i 's/.*setosa,versicolor,virginica/SepalLength,SepalWidth,PetalLength,PetalWidth,classification/g' iris_training.csv iris_test.csv

    Run the train command

    .. code-block:: console
        :test:

        $ dffml train \
            -sources train=csv \
            -source-filename iris_training.csv \
            -model lgbmregressor \
            -model-features \
              SepalLength:float:1 \
              SepalWidth:float:1 \
              PetalLength:float:1 \
              PetalWidth:float:1 \
            -model-predict classification \
            -model-directory model \
            -model-max_depth 3 \
            -model-learning_rate 0.01 \
            -model-n_estimators 200 \
            -model-reg_lambda 1 \
            -model-reg_alpha 0 \
            -model-subsample 1

    Assess the accuracy

    .. code-block:: console
        :test:

        $ dffml accuracy \
            -sources train=csv \
            -source-filename iris_test.csv \
            -model lgbmregressor \
            -model-features \
              SepalLength:float:1 \
              SepalWidth:float:1 \
              PetalLength:float:1 \
              PetalWidth:float:1 \
            -model-predict classification \
            -model-directory model

    Make predictions

    .. code-block:: console
        :test:

        $ dffml predict all \
            -sources train=csv \
            -source-filename iris_test.csv \
            -model lgbmregressor \
            -model-features \
              SepalLength:float:1 \
              SepalWidth:float:1 \
              PetalLength:float:1 \
              PetalWidth:float:1 \
            -model-predict classification \
            -model-directory model

    Python usage

    .. literalinclude:: /../model/lightgbm/examples/regression_example.py
        :test:

    Output

    .. code-block::
        :test:

        $ python regression_example.py

        Test Mean Squared Error: 925.0
        {'Years': 6, 'Expertise': 13, 'Trust': 0.7, 'Salary': 25.0}
        {'Years': 7, 'Expertise': 15, 'Trust': 0.8, 'Salary': 25.0}

    """

    CONFIG = LGBMRegressorModelConfig

    def __init__(self, config) -> None:
        super().__init__(config)
        # The saved model
        self.saved = None
        self.saved_filepath = pathlib.Path(
            self.config.directory, "model.joblib"
        )
        # Load saved model if it exists
        if self.saved_filepath.is_file():
            self.saved = joblib.load(str(self.saved_filepath))

    async def train(self, sources: Sources) -> None:
        """
        Trains and saves a model using the source data, and the config attributes
        """
        # Get data into memory
        xdata = []
        ydata = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if np.isscalar(feature) else feature
                )
            xdata.append(record_data)
            ydata.append(record.feature(self.parent.config.predict.name))
        x_data = pd.DataFrame(xdata)
        y_data = pd.DataFrame(ydata)

        config = self.config._asdict()

        del config["predict"]
        del config["features"]
        del config["directory"]

        # Create model with given configuration
        self.saved = LGBMRegressor(**config)

        # Fitting the model which starts training
        self.saved.fit(x_data, y_data)

        # Save the trained model
        joblib.dump(self.saved, str(self.saved_filepath))

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of the model by gathering predictions of the test data
        and comparing them to the provided results.

        Accuracy is given as an mean squared error (mse)
        """
        if not self.saved:
            raise ModelNotTrained("Train the model before assessing accuracy")

        # Get data
        input_data = await self.get_input_data(sources)

        # Make predictions
        xdata = []
        for record in input_data:
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if np.isscalar(feature) else feature
                )
            xdata.append(record_data)

        predictions = self.saved.predict(pd.DataFrame(xdata))

        # Grab correct values of target
        actuals = [
            input_datum.feature(self.config.predict.name)
            for input_datum in input_data
        ]

        return mean_squared_error(actuals, predictions)

    async def predict(self, sources: Sources) -> AsyncIterator[Record]:
        """
        Uses saved model to make prediction off never seen before data
        """
        if not self.saved:
            raise ModelNotTrained(
                "Train the model first before getting predictions"
            )

        # Grab records and input data (X data)
        input_data = await self.get_input_data(sources)

        # Make predictions
        xdata = []
        for record in input_data:
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if np.isscalar(feature) else feature
                )
            xdata.append(record_data)

        predictions = self.saved.predict(pd.DataFrame(xdata))

        # Update records and yield them to caller
        for record, prediction in zip(input_data, predictions):
            record.predicted(
                self.config.predict.name, float(prediction), float("nan")
            )
            yield record

    async def get_input_data(self, sources: Sources) -> list:
        saved_records = []
        async for record in sources.with_features(
            self.config.features.names()
        ):
            saved_records.append(record)
        return saved_records
