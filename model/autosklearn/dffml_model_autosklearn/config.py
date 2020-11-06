import abc
import pathlib
from typing import Optional, AsyncIterator, List, Dict, Any

import pandas as pd
import joblib as joblib
import autosklearn.estimators

from dffml import (
    Feature,
    Features,
    Sources,
    Record,
    SourcesContext,
    ModelContext,
    ModelNotTrained,
    Accuracy,
    config,
    field,
    make_config_numpy,
)


AutoSklearnConfig = make_config_numpy(
    "AutoSklearnConfig",
    autosklearn.estimators.AutoSklearnEstimator.__init__,
    properties={
        "features": (Features, field("Features to train on")),
        "predict": (Feature, field("Label or the value to be predicted")),
        "directory": (
            pathlib.Path,
            field("Directory where state should be saved",),
        ),
    },
)


class AutoSklearnModelContext(ModelContext):
    """
    Auto-Sklearn based model contexts should derive
    from this model context.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._model = None
        self.features = self._get_feature_names()
        self.path = self.filepath(
            self.parent.config.directory, "trained_model.sav"
        )
        self.load_model()

    def _get_feature_names(self):
        return [name for name in self.parent.config.features.names()]

    async def get_test_records(self, sources: SourcesContext):
        ret_record = []
        async for record in sources.with_features(self.features):
            ret_record.append(record)
        return ret_record

    def filepath(self, directory, file):
        return directory / file

    def load_model(self):
        if self.path.is_file():
            self.model = joblib.load(self.path)

    async def get_predictions(self, data):
        return self.model.predict(data)

    async def train(self, sources: Sources):
        all_data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            all_data.append(record.features())
        df = pd.DataFrame(all_data)
        y_train = df[[self.parent.config.predict.name]]
        x_train = df.drop(columns=[self.parent.config.predict.name])
        self.model.fit(x_train, y_train)
        self.model.fit_ensemble(
            y_train, ensemble_size=self.parent.config.ensemble_size
        )
        joblib.dump(self.model, self.path)

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:
        if not self.model:
            raise ModelNotTrained(
                "Train the model first before getting preictions"
            )
        test_records = await self.get_test_records(sources)
        x_test = pd.DataFrame([record.features() for record in test_records])
        predictions = await self.get_predictions(x_test)
        probability = await self.get_probabilities(x_test)
        target = self.parent.config.predict.name
        for record, predict, prob in zip(
            test_records, predictions, probability
        ):
            record.predicted(target, predict, max(prob))
            yield record

    async def accuracy(self, sources: Sources) -> Accuracy:
        if not self.model:
            raise ModelNotTrained("Train the model before assessing accuracy")
        test_data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            test_data.append(record.features())
        df = pd.DataFrame(test_data)
        y_test = df[[self.parent.config.predict.name]]
        x_test = df.drop(columns=[self.parent.config.predict.name])
        predictions = await self.get_predictions(x_test)
        accuracy = await self.accuracy_score(y_test, predictions)
        return Accuracy(accuracy)

    @property
    @abc.abstractmethod
    def model(self):
        """
        Create the model and return the handle to it.
        """
