import asyncio

from dffml import (
    MeanSquaredErrorAccuracy,
    Features,
    Feature,
    train,
    score,
    predict,
)

from myslr import MySLRModel


async def main():
    # Configure the model
    model = MySLRModel(
        features=Features(Feature("Years", int, 1)),
        predict=Feature("Salary", int, 1),
        location="model",
    )

    # Train the model
    await train(model, "train.csv")

    # Assess accuracy
    scorer = MeanSquaredErrorAccuracy()
    print(
        "Accuracy:",
        await score(model, scorer, Feature("Salary", int, 1), "test.csv"),
    )

    # Make predictions
    async for i, features, prediction in predict(model, "predict.csv"):
        features["Salary"] = prediction["Salary"]["value"]
        print(features)


if __name__ == "__main__":
    asyncio.run(main())
