from typing import Dict, Any

from ..repo import Repo
from ..base import config
from ..model import Model
from ..df.types import Definition
from ..df.base import op


@config
class ModelPredictConfig:
    model: Model

    def __post_init__(self):
        if not isinstance(self.model, Model):
            raise TypeError(
                "model should be an instance of `dffml.model.model.Model`"
            )


@op(
    inputs={
        "features": Definition(
            name="repo_features", primitive="Dict[str, Any]"
        )
    },
    outputs={
        "prediction": Definition(
            name="model_predictions", primitive="Dict[str, Any]"
        )
    },
    config_cls=ModelPredictConfig,
    imp_enter={"model": (lambda self: self.config.model)},
    ctx_enter={"mctx": (lambda self: self.parent.model())},
)
async def model_predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
    async def repos():
        yield Repo("", data={"features": features})
    #TODO see todo in cli.ml.py line 59
    target_name = self.config.model.config.predict.NAME
    async for repo in self.mctx.predict(target_name,repos()):
        return {
            "prediction": {
                target_name: repo.prediction(target_name)
            }
        }
