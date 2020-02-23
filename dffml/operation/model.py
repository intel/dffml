from typing import Dict, Any

from ..record import Record
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
    name="dffml.model.predict",
    inputs={
        "features": Definition(
            name="record_features", primitive="Dict[str, Any]"
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
    async def records():
        yield Record("", data={"features": features})

    async for record in self.mctx.predict(records()):
        return {"prediction": record.predictions()}
