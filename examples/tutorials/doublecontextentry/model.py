import asyncio
from dffml import *

model = SLRModel(
    features=Features(Feature("Years", int, 1),),
    predict=Feature("Salary", int, 1),
    location="tempdir",
)


async def main():
    # Load model and source using double context entry pattern
    # Here we create a memory backed source. Equivlant to what the above example
    # does behind the scenes when passing in dict objects.
    async with model, MemorySource(
        records=[
            Record(i, data={"features": {"Years": i}}) for i in range(6, 8)
        ]
    ) as source:
        async with model() as mctx, source() as sctx:
            # Train the model
            await train(
                mctx,
                {"Years": 0, "Salary": 10},
                {"Years": 1, "Salary": 20},
                {"Years": 2, "Salary": 30},
                {"Years": 3, "Salary": 40},
            )
            # Make predictions
            async for i, features, prediction in predict(mctx, sctx):
                features["Salary"] = round(prediction["Salary"]["value"])
                print(features)


asyncio.run(main())
