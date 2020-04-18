import os
import tempfile

from dffml.record import Record
from dffml.high_level import load, save
from dffml.util.asynctestcase import AsyncTestCase
from dffml.source.ini import INISource, INISourceConfig


class TestINISource(AsyncTestCase):
    async def test_load_fd(self):
        with tempfile.TemporaryDirectory() as testdir:
            self.testfile = os.path.join(testdir, "testfile.ini")
            # Create a source
            source = INISource(
                filename=self.testfile, allowempty=True, readwrite=True,
            )
            # Save some data in the source
            await save(
                source,
                Record("section1", data={"features": {"A": 1, "B": 2,}}),
                Record("section2", data={"features": {"C": 3, "D": 4,}}),
            )
            # Load all the records
            records = [record async for record in load(source)]

            self.assertIsInstance(records, list)
            self.assertEqual(len(records), 2)
            self.assertDictEqual(records[0].features(), {"A": 1, "B": 2})
            self.assertDictEqual(records[1].features(), {"C": 3, "D": 4})
