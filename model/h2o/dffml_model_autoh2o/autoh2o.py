from typing import AsyncIterator
import pandas as pd
import h2o
import os
import sklearn
from h2o.sklearn import H2OAutoMLClassifier, H2OAutoMLRegressor
from .config import AutoH2OConfig
from dffml.model.model import Model
from dffml import (
    Sources,
    Record,
    SourcesContext,
    ModelContext,
    ModelNotTrained,
)
from dffml.util.entrypoint import entrypoint


class AutoH2OModelContext(ModelContext):
    """
    H2O AutoML based model context 
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
        return self.parent.best_model.predict(h2o.H2OFrame(data)).as_data_frame().iloc[:, 0].tolist()

    async def get_best_model(self):
        if not self.is_trained:
            raise ModelNotTrained(
                "Train the model first before getting predictions"
            )
        return self.parent.clf.get_best_model()

    async def accuracy_score(self, y_test, predictions):
        return sklearn.metrics.r2_score(y_test, predictions)

    async def get_probabilities(self, data):
        return [[float("nan")] * len(data)]

    async def train(self, sources: Sources):
        all_data = []
        async for record in sources.with_features(
            self.features + [self.parent.config.predict.name]
        ):
            all_data.append(record.features())

        df = pd.DataFrame(all_data)
        y = self.parent.config.predict.name
        self.parent.clf.fit(df[self.features], pd.DataFrame(df[y]))
        if(self.parent.config.show_leaderboard):
            print(h2o.automl.get_leaderboard(self.parent.clf.estimator, extra_columns = "ALL"))
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
    


@entrypoint("h2o")
class AutoH2OModel(Model):

    r"""
    ``h2o`` / ``AutoH2OModel`` will use ``H2O.ai's`` AutoML Python API
    to train a model for you.

    This is AutoML, it will train and tune hyperparameters from a list of models,
    and return the best model.

    Implemented using ``H2O``'s AutoML Python API (https://docs.h2o.ai/h2o/latest-stable/h2o-docs/automl.html).

    In this version, you must specify the ML task that you wish to perform (either "regression" or "classification").

    Here, we will show a small example using regression. First we create the training and testing datasets:

    **train.csv**

    .. code-block::
        :test:
        :filepath: train.csv

        Feature1,Feature2,TARGET
        0.93,0.68,3.89
        0.24,0.42,1.75
        0.36,0.68,2.75
        0.53,0.31,2.00
        0.29,0.25,1.32
        0.29,0.52,2.14

    **test.csv**

    .. code-block::
        :test:
        :filepath: test.csv

        Feature1,Feature2,TARGET
        0.57,0.84,3.65
        0.95,0.19,2.46
        0.23,0.15,0.93

    Train the model

    .. code-block:: console
        :test:

        $ dffml train \
            -model h2o \
            -model-predict TARGET:float:1 \
            -model-clstype int \
            -sources f=csv \
            -source-filename train.csv \
            -model-features \
              Feature1:float:1 \
              Feature2:float:1 \
            -model-location tempdir \
            -log debug

    Assess the accuracy

    .. code-block:: console
        :test:

        $ dffml accuracy \
            -model h2o \
            -model-predict TARGET:float:1 \
            -model-location tempdir \
            -features TARGET:float:1 \
            -sources f=csv \
            -source-filename test.csv \
            -model-features \
              Feature1:float:1 \
              Feature2:float:1 \
            -scorer mse \
            -log critical
        0.9961211434899032

    Make a file containing the data to predict on

    **predict.csv**

    .. code-block::
        :test:
        :filepath: predict.csv

        Feature1,Feature2
        0.57,0.84

    Make a prediction

    .. code-block:: console
        :test:

        $ dffml predict all \
            -model h2o \
            -model-location tempdir \
            -model-predict TARGET:float:1 \
            -sources iris=csv \
            -model-features \
              Feature1:float:1 \
              Feature2:float:1 \
            -source-filename predict.csv
        [
            {
                "extra": {},
                "features": {
                    "Feature1": 0.57,
                    "Feature2": 0.84
                },
                "key": "0",
                "last_updated": "2020-11-23T05:52:13Z",
                "prediction": {
                    "TARGET": {
                        "confidence": NaN,
                        "value": 3.566799074411392
                    }
                }
            }
        ]

    The model can be trained on large datasets to get better accuracy
    output. The example shown above is to demonstrate the command line usage
    of the model.


    """
 

    def __init__(self, config) -> None:
        super().__init__(config)
        h2o.init()
        self.clf = None
        self.best_model = None
        
        
        

    async def __aenter__(self) -> "AutoH2OModel":
        await super().__aenter__()
        self.path =  os.path.abspath(self.filepath(self.location, "trained_model"))
        self.load_model()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.clf.estimator and self.clf.estimator.leader:
            self.clf.estimator.leader.save_mojo(self.path.__str__())
        await super().__aexit__(exc_type, exc_value, traceback)

    def filepath(self, location, file):
        return location / file

    def load_model(self):
     

        if(os.path.isdir(self.path)):
    
            self.best_model = h2o.import_mojo(self.path.__str__())
            self.is_trained = True
        
        #TO-DO: split into separate regression/classification Models

        if(self.config.task == "regression"):
            self.clf = H2OAutoMLRegressor(
                max_models = self.config.max_models,
                seed=1,
                max_runtime_secs = self.config.max_runtime_secs,
                nfolds = self.config.nfolds,
                max_runtime_secs_per_model = self.config.max_runtime_secs_per_model,
                stopping_metric=self.config.stopping_metric,
                stopping_tolerance=self.config.stopping_tolerance,
                stopping_rounds=self.config.stopping_rounds,
                sort_metric=self.config.sort_metric,
                exclude_algos=self.config.exclude_algos,
                include_algos=self.config.include_algos,
                verbosity=self.config.verbosity,        
            )
        else:
            self.clf = H2OAutoMLClassifier(
                max_models = self.config.max_models,
                seed=1,
                max_runtime_secs = self.config.max_runtime_secs,
                nfolds = self.config.nfolds,
                balance_classes = self.config.balance_classes,
                max_after_balance_size = self.config.max_after_balance_size,
                max_runtime_secs_per_model = self.config.max_runtime_secs_per_model,
                stopping_metric=self.config.stopping_metric,
                stopping_tolerance=self.config.stopping_tolerance,
                stopping_rounds=self.config.stopping_rounds,
                sort_metric=self.config.sort_metric,
                exclude_algos=self.config.exclude_algos,
                include_algos=self.config.include_algos,
                verbosity=self.config.verbosity,
        

            )
        

    CONFIG = AutoH2OConfig
    CONTEXT = AutoH2OModelContext