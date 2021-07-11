import asyncio

from dffml import Model, Features, Feature, train


async def main():
    # Load the model using the entrypoint listed on the model plugins page
    SLRModel = Model.load("slr")

    # Configure the model
    model = SLRModel(
        features=Features(Feature("Years", int, 1)),
        predict=Feature("Salary", int, 1),
        location="slr-model",
    )

    # Train the model
    await train(
        model,
        {"Years": 0, "Expertise": 1, "Trust": 0.1, "Salary": 10},
        {"Years": 1, "Expertise": 3, "Trust": 0.2, "Salary": 20},
    )


if __name__ == "__main__":
    asyncio.run(main())
