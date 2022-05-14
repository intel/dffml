import asyncio

from dffml import Features, Feature, train, accuracy, predict

from dffml_model_orion import OrionModel


async def main():
    # Instantiate the model. We can add hyperparameters too, but in this case
    # we'll leave them to the default hyperparameters
    model = OrionModel()

    # Train the model
    await train(model, "./examples/train.csv")

    # Make predictions
    async for i, features, prediction in predict(
        model, "./examples/predict.csv"
    ):
        print(features["predict"])

    # Check accuracy of our predictions
    print(
        "Accuracy:",
        await accuracy(model, "./examples/predict.csv", "./examples/test.csv"),
    )


if __name__ == "__main__":
    asyncio.run(main())
