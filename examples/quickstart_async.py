import asyncio

from dffml import train, score, predict, Features, Feature
from dffml.accuracy import MeanSquaredErrorAccuracy
from dffml_model_scikit import LinearRegressionModel


async def main():
    model = LinearRegressionModel(
        features=Features(
            Feature("Years", int, 1),
            Feature("Expertise", int, 1),
            Feature("Trust", float, 1),
        ),
        predict=Feature("Salary", int, 1),
        location="tempdir",
    )

    # Train the model
    await train(
        model,
        {"Years": 0, "Expertise": 1, "Trust": 0.1, "Salary": 10},
        {"Years": 1, "Expertise": 3, "Trust": 0.2, "Salary": 20},
        {"Years": 2, "Expertise": 5, "Trust": 0.3, "Salary": 30},
        {"Years": 3, "Expertise": 7, "Trust": 0.4, "Salary": 40},
    )

    # Assess accuracy
    scorer = MeanSquaredErrorAccuracy()
    print(
        "Accuracy:",
        await score(
            model,
            scorer,
            Feature("Salary", int, 1),
            {"Years": 4, "Expertise": 9, "Trust": 0.5, "Salary": 50},
            {"Years": 5, "Expertise": 11, "Trust": 0.6, "Salary": 60},
        ),
    )

    # Make prediction
    async for i, features, prediction in predict(
        model,
        {"Years": 6, "Expertise": 13, "Trust": 0.7},
        {"Years": 7, "Expertise": 15, "Trust": 0.8},
    ):
        features["Salary"] = prediction["Salary"]["value"]
        print(features)


asyncio.run(main())
