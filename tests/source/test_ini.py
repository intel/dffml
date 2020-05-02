import os
from tempfile import TemporaryDirectory

from dffml.record import Record
from dffml.source.ini import INISource
from dffml.high_level import load, save
from dffml.util.asynctestcase import AsyncTestCase


class TestINISource(AsyncTestCase):
    async def test_ini(self):
        with TemporaryDirectory() as testdir:
            self.testfile = os.path.join(testdir, "testfile.ini")
            # Create a source
            source = INISource(
                filename=self.testfile, allowempty=True, readwrite=True
            )
            # Save some data in the source
            await save(
                source,
                Record("section1", data={"features": {"A": 1, "B": 2}}),
                Record("section2", data={"features": {"C": 3, "D": 4}}),
            )
            # Load all the records
            records = [record async for record in load(source)]

            self.assertIsInstance(records, list)
            self.assertEqual(len(records), 2)
            self.assertDictEqual(records[0].features(), {"a": 1, "b": 2})
            self.assertDictEqual(records[1].features(), {"c": 3, "d": 4})
