import pathlib
import statistics
import importlib
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
class daal4pyModelConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on. For SLR only 1 allowed")
    directory: pathlib.Path = field(
        "Directory where state should be saved",
        default=pathlib.Path("~", ".cache", "dffml", "daal4py"),
    )

class daal4pyModelContext(SimpleModelContext):
    """
    Model using tensorflow to make predictions. Handels creation of feature
    columns for real valued, string, and list of real valued features.
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.d4p = importlib.import_module("daal4py")
        self.pd = importlib.import_module("pandas")
        self.np = importlib.import_module("numpy")
        self.features = self.applicable_features
        self.lm = self.d4p.linear_regression_training(interceptFlag=True)
        self.lm_trained = None
        self.lm_predictor = None

    async def train(self, sources: Sources) -> None:
        data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.NAME]
        ):
            feature_data = record.features(
                self.features + [self.parent.config.predict.NAME]
            )
            data.append(feature_data)
        df = self.pd.DataFrame(data)
        xdata = self.np.array(df.drop([self.parent.config.predict.NAME], 1))
        ydata = self.np.array(df[self.parent.config.predict.NAME])
        self.lm_trained = self.lm.compute(xdata, ydata)

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
        
        # Iterate through each record that needs a prediction
        async for record in records:
            feature_data = record.features(self.features)
            df = self.pd.DataFrame(feature_data, index=[0])
            predict = self.np.array(df)
            self.lm_predictor = d4p.linear_regression_prediction()
            prediction = self.lm_predictor.compute(predict, self.lm_trained.model)
            target = self.parent.config.predict.NAME
            record.predicted(
                target, prediction, float("nan")
            )
            # Yield the record to the caller
            yield record


@entrypoint("d4plr")
class daal4pyModel(SimpleModel):
    # The configuration class needs to be set as the CONFIG property
    CONFIG: daal4pyModelConfig
    CONTEXT: daal4pyModelContext


    