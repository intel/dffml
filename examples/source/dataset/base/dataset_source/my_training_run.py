import sys
import pathlib
import unittest

from dffml.noasync import load

from my_training import my_training_dataset


def main():
    # Grab arguments from command line
    url = sys.argv[1]
    cache_dir = pathlib.Path(sys.argv[2])

    # Usage via Source class set as property .source of function
    records = list(
        load(my_training_dataset.source(url=url, cache_dir=cache_dir))
    )

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
    with my_training_dataset(url=url, cache_dir=cache_dir) as source:
        records = list(load(source))
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
    main()
