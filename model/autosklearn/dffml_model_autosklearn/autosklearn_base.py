from typing import AsyncIterator

import joblib
import pandas as pd

from dffml.model.model import Model
from dffml import (
    Sources,
    Record,
    SourcesContext,
    ModelContext,
    ModelNotTrained,
)


class AutoSklearnModel(Model):
    def __init__(self, config):
        super().__init__(config)
        self.model = None

    async def __aenter__(self) -> "AutoSklearnModel":
        await super().__aenter__()
        self.path = self.filepath(self.location, "trained_model.sav",)
        self.load_model()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.model:
            joblib.dump(self.model, self.path)
        await super().__aexit__(exc_type, exc_value, traceback)

    def filepath(self, location, file):
        return location / file

    def load_model(self):
        if self.path.is_file():
            self.model = joblib.load(self.path)
            self.is_trained = True


class AutoSklearnModelContext(ModelContext):
    """
    Auto-Sklearn based model contexts should derive
    from this model context.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.features = self._get_feature_names()

    def _get_feature_names(self):
        return [name for name in self.parent.config.features.names()]

    async def get_test_records(self, sources: SourcesContext):
        ret_record = []
        async for record in sources.with_features(self.features):
            ret_record.append(record)
        return ret_record

    async def get_predictions(self, data):
        return self.parent.model.predict(data)

    async def train(self, sources: Sources):
        all_data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            all_data.append(record.features())
        df = pd.DataFrame(all_data)
        y_train = df[[self.parent.config.predict.name]]
        x_train = df.drop(columns=[self.parent.config.predict.name])
        self.parent.model.fit(x_train, y_train)
        self.parent.model.fit_ensemble(
            y_train, ensemble_size=self.parent.config.ensemble_size
        )
        self.is_trained = True

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:
        if not self.is_trained:
            raise ModelNotTrained(
                "Train the model first before getting predictions"
            )
        test_records = await self.get_test_records(sources)
        x_test = pd.DataFrame(
            [record.features(self.features) for record in test_records]
        )
        predictions = await self.get_predictions(x_test)
        probability = await self.get_probabilities(x_test)
        target = self.parent.config.predict.name
        for record, predict, prob in zip(
            test_records, predictions, probability
        ):
            record.predicted(target, predict, max(prob))
            yield record
