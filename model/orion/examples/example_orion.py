import asyncio

from dffml import Features, Feature, train, accuracy, predict

from dffml_model_orion import OrionModel


async def main():
    # Configure the model
    model = OrionModel(
        data="./tests/train.csv",
        predict="./tests/predict.csv",
        accuracy="./tests/test.csv",
    )

    # Train the model
    await train(model)

    # Make predictions
    async for i, features, prediction in predict(model):
        print(features["predict"])

    # Check accuracy of our predictions
    print("Accuracy:", await accuracy(model))


if __name__ == "__main__":
    asyncio.run(main())
