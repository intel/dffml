import asyncio
from dffml import *

slr_model = SLRModel(
    features=Features(Feature("Years", int, 1)),
    predict=Feature("Salary", int, 1),
)


# This Dataflow takes input from stdio using `AcceptUserInput`
# operation. The string input which corresponds to feature `Years`
# is converted to `int`/`float` by
# `literal_eval` operation.
# `create_mapping` operation creates a mapping using the numeric output
# of `literal_eval` eg. {"Years":34}.
# The mapping is then fed to `model_predict` operation which
# uses the `slr` model trained above to make prediction. The prediction is then printed to
# stdout using `print_output` operation.
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
            inputs={"str_to_eval": [{"get_user_input": "InputData"}]}
        ),
        "create_feature_map": InputFlow(
            inputs={
                "key": ["seed.Years"],
                "value": [{"literal_eval_input": "str_after_eval"}],
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
    # Train the model
    await train(
        slr_model,
        {"Years": 0, "Salary": 10},
        {"Years": 1, "Salary": 20},
        {"Years": 2, "Salary": 30},
        {"Years": 3, "Salary": 40},
    )
    # Run the dataflow
    async for ctx, results in MemoryOrchestrator.run(dataflow, {"inputs": []}):
        pass


if __name__ == "__main__":
    asyncio.run(main())
