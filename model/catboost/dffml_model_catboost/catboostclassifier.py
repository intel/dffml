import pathlib
from typing import AsyncIterator

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score

from dffml.record import Record
from dffml.base import config, field
from dffml.source.source import Sources
from dffml.model.accuracy import Accuracy
from dffml.util.entrypoint import entrypoint
from dffml.feature.feature import Feature, Features
from dffml.model.model import SimpleModel, ModelNotTrained


@config
class CatBoostClassifierModelConfig:
	directory: pathlib.Path = field("Directory where model should be saved")
    features: Features = field("Features on which we train the model")
    predict: Feature = field("Value to be predicted")
    learning_rate: float = field("Learning rate to train with", default=0.03)
    n_estimators: int = field(
        "Number of gradient boosted trees. Equivalent to the number of boosting rounds",
        default=1000,
    )
    max_depth: int = field("Maximium tree depth for base learners", default=6)
    objective: str = field("Objective in training", default="multi:softmax")
    subsample: float = field(
        "Subsample ratio of the training instance", default=1
    )
    thread_count: int = field("The number of threads to use during the training", default=-1)
    classes_count: int = field("The upper limit for the numeric class label. Defines the number of classes for multiclassification",default=None)
    random_seed: int = field("The random seed used for training", default=None(0))


@entrypoint("catboostclassifier")
class CatBoostClassifierModel(SimpleModel):

	CONFIG = CatBoostClassifierModelConfig

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

        self.saved = XGBClassifier(
        n_estimators=self.config.n_estimators,
        max_depth=self.config.max_depth,
        objective=self.config.objective,
        subsample=self.config.subsample,
        thread_count=self.config.thread_count,
        classes_count=self.config.classes_count,
        random_seed=self.config.random_seed,    
        )

        self.saved.fit(x_data, y_data, eval_metric="merror")

        # Save the trained model
        joblib.dump(self.saved, str(self.saved_filepath))


    async def accuracy(self, sources: Sources) -> Accuracy:
        """
        Evaluates the accuracy of the model by gathering predictions of the test data
        and comparing them to the provided results.

        Accuracy is given as an accuracy score
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

        return accuracy_score(actuals, predictions)

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