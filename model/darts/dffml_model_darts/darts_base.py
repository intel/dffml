import pathlib
import importlib
import hashlib
import json
from typing import AsyncIterator, Tuple, Any, NamedTuple


from dffml.record import Record
from dffml.model.accuracy import Accuracy
from dffml.source.source import Sources, SourcesContext
from dffml.model.model import ModelConfig, ModelContext, Model, ModelNotTrained
from dffml.feature.feature import Features, Feature
from dffml.base import field
from darts import TimeSeries
from darts.metrics import mape
import pandas as pd


@config
class DartsConfig(ModelConfig, NamedTuple):
    directory: pathlib.Path = field(
        "Features to train on (myslr only supports one)"
    )
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on")


class DartsContext(ModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        self.np = importlib.import_module("numpy")
        self.pd = importlib.import_module("pandas")
        self.joblib = importlib.import_module("joblib")
        self.features = self.parent.config.features.names()
        self._features_hash = self._feature_predict_hash()
        self.clf = None

    @property
    def confidence(self):
        return self.parent.saved.get(self._features_hash, float("nan"))

    @confidence.setter
    def confidence(self, confidence):
        self.parent.saved[self._features_hash] = confidence

    def _feature_predict_hash(self):
        params = "".join(
            [
                "{}{}".format(k, v)
                for k, v in self.parent.config._asdict().items()
                if k not in ["features", "predict"]
            ]
        )
        return hashlib.sha384(
            "".join([params] + self.features).encode()
        ).hexdigest()

    @property
    def _filepath(self):
        return self.parent.config.directory / "DartsFeatures.joblib"

    async def __aenter__(self):
        if self._filepath.is_file():
            self.clf = self.joblib.load(str(self._filepath))
        else:
            config = self.parent.config._asdict()
            del config["directory"]
            del config["predict"]
            del config["features"]
            self.clf = self.parent.DARTS_MODEL(**config)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def train(self, sources: Sources):
        xdata = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if self.np.isscalar(feature) else feature
                )
            xdata.append(record_data)
        x_data = pd.DataFrame(xdata)
        labels = x_data.columns.values.tolist()
        series = TimeSeries.from_dataframe(x_data, labels[0], labels[1])
        self.logger.info("Number of input records: {}".format(len(xdata)))
        self.clf.fit(series)
        self.joblib.dump(self.clf, str(self._filepath))

    async def accuracy(self, sources: Sources) -> Accuracy:
        if not self._filepath.is_file():
            raise ModelNotTrained("Train model before assessing for accuracy.")
        xdata = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if self.np.isscalar(feature) else feature
                )
            xdata.append(record_data)
        x_data = pd.DataFrame(xdata)
        labels = x_data.columns.values.tolist()
        series = TimeSeries.from_dataframe(x_data, labels[0], labels[1])
        predictions = self.clf.predict(len(series))
        self.logger.debug("Number of input records: {}".format(len(xdata)))
        self.confidence = mape(predictions, series)
        self.logger.debug("Model Accuracy: {}".format(self.confidence))
        return self.confidence

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        xdata = []
        if not self._filepath.is_file():
            raise ModelNotTrained("Train model before prediction.")
        async for record in sources.with_features(self.features):
            record_data = []
            for feature in record.features(self.features).values():
                record_data.extend(
                    [feature] if self.np.isscalar(feature) else feature
                )
            xdata.append(record_data)
            x_data = pd.DataFrame(xdata)
            labels = x_data.columns.values.tolist()
            series = TimeSeries.from_dataframe(x_data, labels[0], labels[1])
            predictions = self.clf.predict(len(series))
            target = self.parent.config.predict.name
            record.predicted(target, float(predictions), self.confidence)
            yield record


@entrypoint("darts")
class Darts(Model):
    CONFIG = DartsConfig
    CONTEXT = DartsContext

    def __init__(self, config) -> None:
        super().__init__(config)
        self.saved = {}

    @property
    def _filepath(self):
        return self.config.directory / "Darts.json"

    async def __aenter__(self) -> "Darts":
        if self._filepath.is_file():
            self.saved = json.loads(self._filepath.read_text())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._filepath.write_text(json.dumps(self.saved))
