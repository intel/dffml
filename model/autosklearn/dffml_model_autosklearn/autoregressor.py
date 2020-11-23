import sklearn.metrics
import autosklearn.regression

from dffml.model.model import Model
from dffml.util.entrypoint import entrypoint

from .config import AutoSklearnConfig, AutoSklearnModelContext


class AutoSklearnRegressorModelContext(AutoSklearnModelContext):
    def __init__(self, parent):
        super().__init__(parent)

    @property
    def model(self):
        """
        Generates or loads a model
        """
        if self._model is not None:
            return self._model
        config = self.parent.config._asdict()
        del config["predict"]
        del config["features"]
        del config["directory"]
        self._model = autosklearn.regression.AutoSklearnRegressor(**config)
        return self._model

    @model.setter
    def model(self, model):
        """
        Loads a model if already trained previously
        """
        self._model = model

    async def accuracy_score(self, y_test, predictions):
        return sklearn.metrics.r2_score(y_test, predictions)

    async def get_probabilities(self, data):
        return [[float("nan")] * len(data)]


@entrypoint("autoregressor")
class AutoSklearnRegressorModel(Model):
    r"""
    ``autoregressor`` / ``AutoSklearnRegressorModel`` will use ``auto-sklearn``
    to train the a scikit model for you.

    This is AutoML, it will tune hyperparameters for you.

    Implemented using `AutoSklearnRegressor <https://automl.github.io/auto-sklearn/master/api.html#regression>`_.

    First we create the training and testing datasets

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
            -model autoregressor \
            -model-predict TARGET:float:1 \
            -model-clstype int \
            -sources f=csv \
            -source-filename train.csv \
            -model-features \
              Feature1:float:1 \
              Feature2:float:1 \
            -model-time_left_for_this_task 120 \
            -model-per_run_time_limit 30 \
            -model-ensemble_size 50 \
            -model-delete_tmp_folder_after_terminate False \
            -model-directory tempdir \
            -log debug

    Assess the accuracy

    .. code-block:: console
        :test:

        $ dffml accuracy \
            -model autoregressor \
            -model-predict TARGET:float:1 \
            -model-directory tempdir \
            -sources f=csv \
            -source-filename test.csv \
            -model-features \
              Feature1:float:1 \
              Feature2:float:1 \
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
            -model autoregressor \
            -model-directory tempdir \
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

    Example usage of using the model from Python

    **run.py**

    .. literalinclude:: /../model/autosklearn/examples/autoregressor.py
        :test:
        :filepath: run.py

    Run the file

    .. code-block:: console
        :test:

        $ python run.py
        Accuracy: 0.9961211434899032
        {'Feature1': 0.57, 'Feature2': 0.84, 'TARGET': 3.6180416345596313}
    """
    CONFIG = AutoSklearnConfig
    CONTEXT = AutoSklearnRegressorModelContext
