import asyncio

from dffml import Features, Feature, train, accuracy, predict

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
    print("Accuracy:", await accuracy(model, "test.csv"))

    # Make predictions
    async for i, features, prediction in predict(model, "predict.csv"):
        features["Salary"] = prediction["Salary"]["value"]
        print(features)


if __name__ == "__main__":
    asyncio.run(main())
