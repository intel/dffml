import asyncio

from dffml.noasync import train
from dffml import Features, DefFeature
from dffml.operation.output import GetSingle
from dffml.df.memory import MemoryOrchestrator
from dffml.df.types import DataFlow, Input, InputFlow
from dffml.operation.model import model_predict, ModelPredictConfig
from dffml.operation.io import AcceptUserInput, print_output

from dffml_model_scikit import LinearRegressionModel

scikit_model = LinearRegressionModel(
    features=Features(
        DefFeature("Years", int, 1),
        DefFeature("Expertise", int, 1),
        DefFeature("Trust", float, 1),
    ),
    predict=DefFeature("Salary", int, 1),
)

# TODO Training should be in different file, only prediction
# should be here?
# TODO decide on the stdin input format, if its like {"Years": 0, "Expertise": 1, "Trust": 0.1, "Salary": 10}
# then literal_eval or something.. ask John
train(
    scikit_model,
    {"Years": 0, "Expertise": 1, "Trust": 0.1, "Salary": 10},
    {"Years": 1, "Expertise": 3, "Trust": 0.2, "Salary": 20},
    {"Years": 2, "Expertise": 5, "Trust": 0.3, "Salary": 30},
    {"Years": 3, "Expertise": 7, "Trust": 0.4, "Salary": 40},
)
dataflow = DataFlow(
    operations={
        "user_input": AcceptUserInput,
        "modelprediction": model_predict,
        "print_output": print_output,
        "get_single": GetSingle,
    },
    configs={"modelprediction": ModelPredictConfig(model=scikit_model)},
    flow={
        "modelprediction": InputFlow(
            inputs={"features": [{"user_input": "InputData"}]}
        ),
        "print_output": InputFlow(
            inputs={"data": [{"modelprediction": "prediction"}]}
        ),
    },
)
dataflow.seed.append(
    Input(
        value=[model_predict.op.outputs["prediction"].name],
        definition=GetSingle.op.inputs["spec"],
    )
)


async def main():
    async for ctx, results in MemoryOrchestrator.run(dataflow, {"inputs": []}):
        print("Finished")


asyncio.run(main())
