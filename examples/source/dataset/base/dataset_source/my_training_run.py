import sys
import pathlib
import unittest
import asyncio

from dffml import load

from my_training import my_training_dataset


async def main():
    # Grab arguments from command line
    url = sys.argv[1]
    cache_dir = pathlib.Path(sys.argv[2])

    # Usage via Source class set as property .source of function
    records = [
        record
        async for record in load(
            my_training_dataset.source(url=url, cache_dir=cache_dir)
        )
    ]

    # Create a test case to do comparisons
    tc = unittest.TestCase()

    tc.assertEqual(len(records), 5)
    tc.assertDictEqual(
        records[0].export(),
        {
            "key": "0",
            "features": {"feed": 0.0, "face": 0, "dead": 0, "beef": 0},
            "extra": {},
        },
    )

    # Usage as context manager to create source
    async with my_training_dataset(url=url, cache_dir=cache_dir) as source:
        records = records = [record async for record in load(source)]
        tc.assertEqual(len(records), 5)
        tc.assertDictEqual(
            records[2].export(),
            {
                "key": "2",
                "features": {"feed": 0.2, "face": 2, "dead": 20, "beef": 200},
                "extra": {},
            },
        )


if __name__ == "__main__":
    asyncio.run(main())
