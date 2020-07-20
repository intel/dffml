import pathlib
import importlib

from operator import sub
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
    SourcesContext,
)


@config
class DAAL4PyLRModelConfig:
    predict: Feature = field("Label or the value to be predicted")
    features: Features = field("Features to train on. For SLR only 1 allowed")
    directory: pathlib.Path = field("Directory where state should be saved",)


@entrypoint("daal4pylr")
class DAAL4PyLRModel(SimpleModel):
    """
    Implemented using daal4py.

    First we create the training and testing datasets

    .. literalinclude:: /../model/daal4py/examples/lr/train_data.sh

    .. literalinclude:: /../model/daal4py/examples/lr/test_data.sh

    Train the model

    .. literalinclude:: /../model/daal4py/examples/lr/train.sh

    Assess the accuracy

    .. literalinclude:: /../model/daal4py/examples/lr/accuracy.sh

    Output

    .. code-block::

        0.6666666666666666


    Make a prediction

    .. literalinclude:: /../model/daal4py/examples/lr/predict.sh

    Output

    .. code-block:: json

        [
            {
                "extra": {},
                "features": {
                    "ans": 1,
                    "f1": 0.8
                },
                "key": "0",
                "last_updated": "2020-07-22T02:53:11Z",
                "prediction": {
                    "ans": {
                        "confidence": NaN,
                        "value": 1.1907472649730522
                    }
                }
            }
        ]





    Example usage of daal4py Linear Regression model using python API

    .. literalinclude:: /../model/daal4py/examples/lr/textclassifier.py
    """

    CONFIG = DAAL4PyLRModelConfig

    def __init__(self, config) -> None:
        super().__init__(config)
        self.pd = importlib.import_module("pandas")
        self.np = importlib.import_module("numpy")
        self.d4p = importlib.import_module("daal4py")
        self.joblib = importlib.import_module("joblib")
        self.lm = self.d4p.linear_regression_training(
            interceptFlag=True, streaming=True
        )
        self.lm_predictor = self.d4p.linear_regression_prediction()
        self.ac_predictor = self.d4p.linear_regression_prediction()
        self.path = self.filepath(
            self.parent.config.directory, "trained_model.sav"
        )
        self.lm_trained = None
        self.load_model()

    def compare(self, alist, bfloat):
        result = []
        for element in alist:
            if element <= bfloat:
                result.append(True)
            else:
                result.append(False)
        return result

    def load_model(self):
        if self.path.is_file():
            self.lm_trained = self.joblib.load(self.path)

    def filepath(self, directory, file_name):
        return directory / file_name

    async def train(self, sources: Sources) -> None:
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            feature_data = record.features(
                self.features + [self.parent.config.predict.name]
            )
            df = self.pd.DataFrame(feature_data, index=[0])
            xdata = df.drop([self.parent.config.predict.name], 1)
            ydata = df[self.parent.config.predict.name]
            self.lm.compute(xdata, ydata)
        self.lm_trained = self.lm.finalize().model
        self.joblib.dump(self.lm_trained, self.path)

    async def accuracy(self, sources: Sources) -> Accuracy:
        if self.lm_trained is None:
            raise ModelNotTrained("Train model before assessing for accuracy.")
        feature_data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            feature_data.append(
                record.features(
                    self.features + [self.parent.config.predict.name]
                )
            )
        df = self.pd.DataFrame(feature_data)
        xdata = df.drop([self.parent.config.predict.name], 1)
        ydata = df[self.parent.config.predict.name]
        preds = self.ac_predictor.compute(xdata, self.lm_trained)
        # Calculate accuracy with an error margin of 0.1
        accuracy_val = sum(
            self.compare(
                list(map(abs, map(sub, ydata, preds.prediction))), 0.1
            )
        ) / len(ydata)
        return Accuracy(accuracy_val)

    async def predict(
        self, sources: SourcesContext
    ) -> AsyncIterator[Tuple[Record, Any, float]]:
        # Iterate through each record that needs a prediction
        if self.lm_trained is None:
            raise ModelNotTrained("Train model before prediction.")
        async for record in sources.with_features(
            self.parent.config.features.names()
        ):
            feature_data = record.features(self.features)
            predict = self.pd.DataFrame(feature_data, index=[0])
            preds = self.lm_predictor.compute(predict, self.lm_trained)
            target = self.parent.config.predict.name
            if preds.prediction.size == 1:
                prediction = preds.prediction.flat[0]
            else:
                prediction = preds.prediction
            record.predicted(target, prediction, float("nan"))
            # Yield the record to the caller
            yield record
