import asyncio

from dffml.noasync import train
from dffml import Features, DefFeature
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.mapping import create_mapping
from dffml.operation.preprocess import literal_eval
from dffml.df.types import DataFlow, Input, InputFlow
from dffml.operation.io import AcceptUserInput, print_output
from dffml.operation.model import model_predict, ModelPredictConfig
from dffml.model.slr import SLRModel

slr_model = SLRModel(
    features=Features(DefFeature("Years", int, 1),),
    predict=DefFeature("Salary", int, 1),
)

train(
    slr_model,
    {"Years": 0, "Salary": 10},
    {"Years": 1, "Salary": 20},
    {"Years": 2, "Salary": 30},
    {"Years": 3, "Salary": 40},
)
dataflow = DataFlow(
    operations={
        "get_user_input": AcceptUserInput,
        "literal_eval_input": literal_eval,
        "create_feature_map": create_mapping,
        "predict_using_model": model_predict,
        "print_predictions": print_output,
    },
    configs={"predict_using_model": ModelPredictConfig(model=slr_model)},
    flow={
        "literal_eval_input": InputFlow(
            inputs={"InputStr": [{"get_user_input": "InputData"}]}
        ),
        "create_feature_map": InputFlow(
            inputs={
                "key": ["seed.Years"],
                "value": [{"literal_eval_input": "EvaluatedStr"}],
            }
        ),
        "predict_using_model": InputFlow(
            inputs={"features": [{"create_feature_map": "mapping"}]}
        ),
        "print_predictions": InputFlow(
            inputs={"data": [{"predict_using_model": "prediction"}]}
        ),
    },
)
dataflow.seed.append(
    Input(
        value="Years",
        definition=create_mapping.op.inputs["key"],
        origin="seed.Years",
    )
)


async def main():
    async for ctx, results in MemoryOrchestrator.run(dataflow, {"inputs": []}):
        print("Finished")


asyncio.run(main())
