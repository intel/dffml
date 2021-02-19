import asyncio
import dataclasses

from dffml import Model


async def main():
    # Load each model class
    for model_cls in [Model.load("slr")]:
        # Print the class
        print(model_cls)
        # Print all the config properties
        for field in dataclasses.fields(model_cls.CONFIG):
            print(f"    {field.name}: {field.metadata['description']}")


if __name__ == "__main__":
    asyncio.run(main())
