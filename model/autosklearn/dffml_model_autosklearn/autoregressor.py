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
    CONFIG = AutoSklearnConfig
    CONTEXT = AutoSklearnRegressorModelContext
