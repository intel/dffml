import os
from tempfile import TemporaryDirectory

from dffml.high_level import load, save
from dffml.record import Record
from dffml.util.asynctestcase import AsyncTestCase
from dffml_source_xlsx.xlsx import XLSXSource


class TestXLSXSource(AsyncTestCase):
    async def test_xlsx_records(self):
        # Test case for xlsx load and save
        with TemporaryDirectory() as testdir:
            self.testfile = os.path.join(testdir, "testfile.xlsx")
            # Create a source
            source = XLSXSource(
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
            self.assertDictEqual(records[0].features(), {"A": 1, "B": 2})
            self.assertDictEqual(records[1].features(), {"A": 3, "B": 4})
