import sklearn.metrics
import autosklearn.classification

from dffml.model.model import Model
from dffml.util.entrypoint import entrypoint

from .config import AutoSklearnConfig, AutoSklearnModelContext


class AutoSklearnClassifierModelContext(AutoSklearnModelContext):
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
        self._model = autosklearn.classification.AutoSklearnClassifier(
            **config
        )
        return self._model

    @model.setter
    def model(self, model):
        """
        Loads a model if already trained previously
        """
        self._model = model

    async def accuracy_score(self, y_test, predictions):
        return sklearn.metrics.accuracy_score(y_test, predictions)

    async def get_probabilities(self, data):
        return self.model.predict_proba(data)


@entrypoint("autoclassifier")
class AutoSklearnClassifierModel(Model):
    CONFIG = AutoSklearnConfig
    CONTEXT = AutoSklearnClassifierModelContext
