import autosklearn.classification

from dffml.util.entrypoint import entrypoint

from .config import AutoSklearnConfig
from .autosklearn_base import AutoSklearnModelContext, AutoSklearnModel


class AutoSklearnClassifierModelContext(AutoSklearnModelContext):
    def __init__(self, parent):
        super().__init__(parent)
        if self.parent.model is None:
            config = self.parent.config._asdict()
            del config["predict"]
            del config["features"]
            del config["location"]
            self.parent.model = autosklearn.classification.AutoSklearnClassifier(
                **config
            )

    async def get_probabilities(self, data):
        return self.parent.model.predict_proba(data)


@entrypoint("autoclassifier")
class AutoSklearnClassifierModel(AutoSklearnModel):
    CONFIG = AutoSklearnConfig
    CONTEXT = AutoSklearnClassifierModelContext
