import os
import pathlib
from typing import AsyncIterator, List

import h2o
import numpy as np
import pandas as pd
from dffml.base import config, field
from dffml.feature.feature import Feature, Features
from dffml.model.accuracy import Accuracy
from dffml.model.model import ModelNotTrained, SimpleModel
from dffml.record import Record
from dffml.source.source import Sources
from dffml.util.entrypoint import entrypoint
from h2o.automl import H2OAutoML
from sklearn.metrics import mean_squared_error


@config
class H2oAutoMLModelConfig:
    features: Features = field("Features on which we train  the model")
    predict: Feature = field("Label or the value to be predicted")
    directory: pathlib.Path = field("Directory where state should be saved")
    max_runtime_secs: int = field(
        "The maximum time that the AutoML process will run", default=0
    )
    max_models: int = field(
        "Maximum number of models to build in AutoML run", default=None
    )
    nfolds: int = field(
        "Number of folds for k-fold cross-validation", default=5
    )
    balance_classes: bool = field(
        "Oversampling on minority classes should be performed or not",
        default=False,
    )
    max_after_balance_size: int = field(
        "Maximum relative size of training set after performing oversampling",
        default=5,
    )
    max_runtime_secs_per_model: int = field(
        "Maximum time to train individual model in AutoML", default=0
    )
    stopping_metric: str = field(
        "Metric used for stopping criteria", default="AUTO"
    )
    stopping_tolerance: float = field(
        "Specifies the relative tolerance for the metric-based stopping",
        default=0.001,
    )
    stopping_rounds: int = field(
        "Stop training when metric doesn't improve max of stopping_rounds",
        default=3,
    )
    sort_metric: str = field(
        "Metric used to sort the leaderboard", default="AUTO"
    )
    project_name: str = field("Name of AutoML project", default=None)
    exclude_algos: List[str] = field(
        "Algorithm to skip during training", default=None
    )
    include_algos: List[str] = field(
        "Algorithm to be used during training", default=None
    )
    keep_cross_validation_predictions: bool = field(
        "Save each of the predictions during cross-validation", default=False
    )
    keep_cross_validation_models: bool = field(
        "keep models of cross-validation", default=False
    )
    keep_cross_validation_fold_assignment: bool = field(
        "Preserve the cross-validation fold assignment", default=False
    )
    verbosity: str = field("Print the backend messages", default=None)
    export_checkpoints_dir: str = field(
        "Specify the directory to save the models", default=None
    )
    show_leaderboard: bool = field(
        "Print the leaderboard after the building the models in AutoML",
        default=False,
    )


@entrypoint("h2oautoml")
class H2oAutoMLModel(SimpleModel):
    r"""
    H2O’s AutoML can be used for automating the machine learning workflow,
    which includes automatic training and tuning of many models within a user-specified time-limit

    Examples
    --------

    Command line usage

    First download the training and test files, change the headers to DFFML
    format.

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
            -model h2oautoml \
            -model-features \
              SepalLength:float:1 \
              SepalWidth:float:1 \
              PetalLength:float:1 \
              PetalWidth:float:1 \
            -model-predict classification \
            -model-directory model \
            -model-max_models 5

    Assess the accuracy

    .. code-block:: console
        :test:

        $ dffml accuracy \
            -sources train=csv \
            -source-filename iris_test.csv \
            -model h2oautoml \
            -model-features \
              SepalLength:float:1 \
              SepalWidth:float:1 \
              PetalLength:float:1 \
              PetalWidth:float:1 \
            -model-predict classification \
            -model-directory model
            
    Output

    .. code-block::

        accuracy: 0.8685475825


    Make predictions

    .. code-block:: console
        :test:

        $ dffml predict all \
            -sources train=csv \
            -source-filename iris_test.csv \
            -model h2oautoml \
            -model-features \
              SepalLength:float:1 \
              SepalWidth:float:1 \
              PetalLength:float:1 \
              PetalWidth:float:1 \
            -model-predict classification \
            -model-directory model

    Python usage

    **run.py**

    .. literalinclude:: ../model/h2oautoml/examples/example_h2oautoml.py
        :test:
        :filepath: run.py

    Output

    .. code-block::
        :test:

        $ python run.py
        Test RMSE: 20.0897
        Training RMSE: 0.7263
    """

    # The configuration class needs to be set as the CONFIG property
    CONFIG = H2oAutoMLModelConfig

    def __init__(self, config) -> None:
        super().__init__(config)

        # Initialize and connect to h2o
        h2o.init()

        # The saved model
        self.saved = None
        self.saved_filepath = pathlib.Path(self.config.directory)

        # Load saved model if it exists
        try:
            path = (
                str(self.saved_filepath)
                + "/"
                + str(os.listdir(str(self.saved_filepath))[1])
            )
            print("\n\n", path)
            self.saved = h2o.load_model(path)
        except:
            pass

    async def train(self, sources: Sources) -> None:
        """
        Trains and saves a model using the source data, and the config attributes
        """

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
        y_data.columns = ["toPredict"]

        train = pd.concat([x_data, y_data], axis=1)

        # Feature name and predict column name
        xcol = list(x_data.columns)
        ycol = "toPredict"

        # Load data as h2o frames
        train = h2o.H2OFrame(train)

        self.saved = H2OAutoML(
            max_runtime_secs=self.config.max_runtime_secs,
            max_models=self.config.max_models,
            nfolds=self.config.nfolds,
            balance_classes=self.config.balance_classes,
            max_after_balance_size=self.config.max_after_balance_size,
            max_runtime_secs_per_model=self.config.max_runtime_secs_per_model,
            stopping_metric=self.config.stopping_metric,
            stopping_tolerance=self.config.stopping_tolerance,
            stopping_rounds=self.config.stopping_rounds,
            sort_metric=self.config.sort_metric,
            project_name=self.config.project_name,
            exclude_algos=self.config.exclude_algos,
            include_algos=self.config.include_algos,
            keep_cross_validation_predictions=self.config.keep_cross_validation_predictions,
            keep_cross_validation_models=self.config.keep_cross_validation_models,
            keep_cross_validation_fold_assignment=self.config.keep_cross_validation_fold_assignment,
            export_checkpoints_dir=self.config.export_checkpoints_dir,
            verbosity=self.config.verbosity,
        )

        self.saved.train(x=xcol, y=ycol, training_frame=train)

        if self.config.show_leaderboard:
            self.logger.info(str(self.saved.leaderboard))

        # Get model ids from leader_board of h2o's Automl
        leader_board = self.saved.leaderboard
        model_ids = list(leader_board["model_id"].as_data_frame().iloc[:, 0])

        # Get leader model of the leader_board
        mdl = h2o.get_model(model_ids[0])

        # Save the leader model
        h2o.save_model(model=mdl, path=str(self.saved_filepath), force=True)

    async def accuracy(self, sources: Sources) -> Accuracy:
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

        xdata = h2o.H2OFrame(pd.DataFrame(xdata))

        predictions = self.saved.predict(xdata)
        predictions = h2o.as_list(predictions)
        actuals = [
            input_datum.feature(self.config.predict.name)
            for input_datum in input_data
        ]

        return mean_squared_error(actuals, predictions["predict"])

    async def predict(self, sources: Sources) -> AsyncIterator[Record]:
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

        xdata = h2o.H2OFrame(pd.DataFrame(xdata))

        predictions = self.saved.predict(xdata)
        predictions = h2o.as_list(predictions)["predict"]
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
