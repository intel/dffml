# Co-authored-by: Oliver O'Brien <oliverobrien111@gmail.com>
# Co-authored-by: John Andersen <johnandersenpdx@gmail.com>
# Co-authored-by: Soren Andersen <sorenpdx@gmail.com>
import pathlib
from typing import AsyncIterator

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import r2_score

from dffml.record import Record
from dffml.base import config, field
from dffml.source.source import Sources
from dffml.model.accuracy import Accuracy
from dffml.util.entrypoint import entrypoint
from dffml.feature.feature import Feature, Features
from dffml.model.model import SimpleModel, ModelNotTrained


@config
class XGBRegressorModelConfig:
    directory: pathlib.Path = field("Directory where model should be saved")
    features: Features = field("Features on which we train the model")
    predict: Feature = field("Value to be predicted")
    learning_rate: float = field("Learning rate to train with", default=0.05)
    n_estimators: int = field(
        "Number of gradient boosted trees. Equivalent to the number of boosting rounds",
        default=1000,
    )
    max_depth: int = field("Maximium tree depth for base learners", default=6)
    subsample: float = field(
        "Subsample ratio of the training instance", default=1
    )
    gamma: float = field(
        "Minimium loss reduction required to make a furthre partition on a leaf node",
        default=0,
    )
    n_jobs: int = field(
        "Number of parallel threads used to run xgboost", default=-1
    )
    colsample_bytree: float = field(
        "Subsample ratio of columns when constructing each tree", default=1
    )
    booster: str = field(
        "Specify which booster to use: gbtree, gblinear or dart",
        default="gbtree",
    )
    min_child_weight: float = field(
        "Minimum sum of instance weight(hessian) needed in a child", default=0
    )
    reg_lambda: float = field(
        "L2 regularization term on weights. Increasing this value will make model more conservative",
        default=1,
    )
    reg_alpha: float = field(
        "L1 regularization term on weights. Increasing this value will make model more conservative",
        default=0,
    )


@entrypoint("xgbregressor")
class XGBRegressorModel(SimpleModel):
    """
    Model using xgboost to perform regression prediction via gradient boosted trees
    XGBoost is a leading software library for working with standard tabular data (the type of data you store in Pandas DataFrames,
    as opposed to more exotic types of data like images and videos). With careful parameter tuning, you can train highly accurate models.

    Examples
    --------

    Python usage

    .. literalinclude:: /../model/xgboost/examples/diabetesregression.py

    Output

    .. code-block::

        Test accuracy: 0.6669655406927468
        Training accuracy: 0.819782501866115
    """

    CONFIG = XGBRegressorModelConfig

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

        self.saved = xgb.XGBRegressor(
            n_estimators=self.config.n_estimators,
            learning_rate=self.config.learning_rate,
            max_depth=self.config.max_depth,
            subsample=self.config.subsample,
            gamma=self.config.gamma,
            n_jobs=self.config.n_jobs,
            colsample_bytree=self.config.colsample_bytree,
            booster=self.config.booster,
            min_child_weight=self.config.min_child_weight,
            reg_lambda=self.config.reg_lambda,
            reg_alpha=self.config.reg_alpha,
        )

        self.saved.fit(x_data, y_data)

        # Save the trained model
        joblib.dump(self.saved, str(self.saved_filepath))

    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of the model by gathering predictions of the test data
        and comparing them to the provided results.

        Accuracy is given as an R^2 regression score
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

        actuals = [
            input_datum.feature(self.config.predict.name)
            for input_datum in input_data
        ]

        return r2_score(actuals, predictions)

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
