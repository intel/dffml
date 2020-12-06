from typing import Dict, Any

from ..record import Record
from ..base import config
from ..model import Model
from ..df.types import Definition
from ..df.base import op
from ..source.source import Sources
from ..source.memory import MemorySource, MemorySourceConfig


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
    """
    Predict using dffml models.

    Parameters
    ----------
    features : dict
        A dictionary contaning feature name and feature value.

    Returns
    -------
    dict
        A dictionary containing prediction.

    Examples
    --------

    The following example shows how to use model_predict.

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> slr_model = SLRModel(
    ...     features=Features(Feature("Years", int, 1)),
    ...     predict=Feature("Salary", int, 1),
    ...     directory="tempdir",
    ... )
    >>> dataflow = DataFlow(
    ...     operations={
    ...         "prediction_using_model": model_predict,
    ...         "get_single": GetSingle,
    ...     },
    ...     configs={"prediction_using_model": ModelPredictConfig(model=slr_model)},
    ... )
    >>> dataflow.seed.append(
    ...     Input(
    ...         value=[model_predict.op.outputs["prediction"].name],
    ...         definition=GetSingle.op.inputs["spec"],
    ...     )
    ... )
    >>>
    >>> async def main():
    ...     await train(
    ...         slr_model,
    ...         {"Years": 0, "Salary": 10},
    ...         {"Years": 1, "Salary": 20},
    ...         {"Years": 2, "Salary": 30},
    ...         {"Years": 3, "Salary": 40},
    ...     )
    ...     inputs = [
    ...        Input(
    ...            value={"Years": 4}, definition=model_predict.op.inputs["features"],
    ...        )
    ...     ]
    ...     async for ctx, results in MemoryOrchestrator.run(dataflow, inputs):
    ...         print(results)
    >>>
    >>> asyncio.run(main())
    {'model_predictions': {'Salary': {'confidence': 1.0, 'value': 50}}}
    """

    async with Sources(
        MemorySource(
            MemorySourceConfig(
                records=[Record("", data={"features": features})]
            )
        )
    ) as source:
        async with source() as sctx:
            async for record in self.mctx.predict(sctx):
                return {"prediction": record.predictions()}
