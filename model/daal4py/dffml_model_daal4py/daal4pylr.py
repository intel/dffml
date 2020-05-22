import pathlib
import statistics
import importlib
import hashlib
import os

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


@config
class DAAL4PyLRModelConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on. For SLR only 1 allowed")
    directory: pathlib.Path = field(
        "Directory where state should be saved",
        default=pathlib.Path("~", ".cache", "dffml", "daal4py"),
    )


@entrypoint("daal4pylr")
class DAAL4PyLRModel(SimpleModel):
    CONFIG = DAAL4PyLRModelConfig

    def __init__(self, config) -> None:
        super().__init__(config)
        self.pd = importlib.import_module("pandas")
        self.np = importlib.import_module("numpy")
        self.d4p = importlib.import_module("daal4py")
        self.features = self.features.names()
        self.lm = self.d4p.linear_regression_training(interceptFlag=True, streaming = True)
        self.lm_predictor = self.d4p.linear_regression_prediction()
        self.path = self.filepath(self.parent.config.directory, "trained_model.sav")
        self.lm_trained = None
        self.load_model()

    def load_model(self):
        if self.path.is_file():
            self.lm_trained = self.joblib.load(self.path)

    def filepath(self, directory, file_name):
        return directory / file_name

    async def train(self, sources: Sources) -> None:
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            xdata = record.features(self.features)
            ydata = record.features(self.parent.config.predict.name)
            self.lm.compute(xdata, ydata)
        self.lm_trained = lm.finalize()
        self.joblib.dump(self.lm_trained, self.path)

    async def accuracy(self, sources: Sources) -> Accuracy:
        if self.lm_trained is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")
        data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            feature_data = record.features(
                self.features + [self.parent.config.predict.name]
            )
            data.append(feature_data)
        df = self.pd.DataFrame(data)
        xdata = self.np.array(df.drop([self.parent.config.predict.name], 1))
        ydata = self.np.array(df[self.parent.config.predict.name])
        prediction = self.lm_predictor.compute(xdata, self.lm_trained.model)
        accuracy_val = 100 * sum((prediction == ydata))/len(ydata)
        return Accuracy(accuracy_val)

    async def predict(
        self, records: AsyncIterator[Record]
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        # Iterate through each record that needs a prediction
        if self.lm_trained is None:
            raise ModelNotTrained("Train model before preiction.")
        async for record in records:
            feature_data = record.features(self.features)
            df = self.pd.DataFrame(feature_data, index=[0])
            predict = self.np.array(df)
            prediction = self.lm_predictor.compute(predict, self.lm_trained.model)
            target = self.parent.config.predict.name
            record.predicted(
                target, prediction, float("nan")
            )
            # Yield the record to the caller
            yield record