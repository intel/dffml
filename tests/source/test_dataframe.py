import os
import pandas as pd

from dffml import (
    Record,
    load,
    save,
    AsyncTestCase,
    DataFrameSource,
    DataFrameSourceConfig,
)


class TestDataFrameSource(AsyncTestCase):
    async def test_dataframe(self):

        mydict = [{"A": 1, "B": 2, "C": 3}]
        df = pd.DataFrame(mydict)

        source = DataFrameSource(
            DataFrameSourceConfig(dataframe=df, predictions=["C"],)
        )
        # Save some data in the source
        await save(
            source,
            Record("1", data={"features": {"A": 4, "B": 5, "C": 6}}),
            Record("2", data={"features": {"A": 7, "B": 8, "C": 9}}),
        )

        # Load all the records
        records = [record async for record in load(source)]

        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 3)
        self.assertDictEqual(records[0].features(), {"A": 1, "B": 2, "C": 3})
        self.assertDictEqual(records[1].features(), {"A": 4, "B": 5, "C": 6})
        self.assertDictEqual(records[2].features(), {"A": 7, "B": 8, "C": 9})

    async def test_update(self):

        mydict = [{"A": 1, "B": 2, "C": 3}]
        df = pd.DataFrame(mydict)

        source = DataFrameSource(
            DataFrameSourceConfig(dataframe=df, predictions=["C"],)
        )
        # Save some data in the source
        await save(
            source,
            Record("1", data={"features": {"A": 4, "B": 5, "C": 6}}),
            Record("2", data={"features": {"A": 7, "B": 8, "C": 9}}),
        )

        await save(
            source, Record("2", data={"features": {"A": 15, "B": 16, "C": 14}})
        )

        records = [record async for record in load(source)]
        self.assertEqual(len(records), 3)
        self.assertDictEqual(records[0].features(), {"A": 1, "B": 2, "C": 3})
        self.assertDictEqual(records[1].features(), {"A": 4, "B": 5, "C": 6})
        self.assertDictEqual(
            records[2].features(), {"A": 15, "B": 16, "C": 14}
        )
