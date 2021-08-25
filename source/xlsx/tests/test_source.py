from dffml.util.asynctestcase import AsyncTestCase
from tempfile import TemporaryDirectory
import os, random
from dffml.high_level import load, save
from dffml.record import Record
from dffml_source_xlsx.xlsx import XLSXSourceConfig, XLSXSource


class TestXLSXSource(AsyncTestCase):
    async def test_xlsx_source(self):
        # Use a temporary file for testing.
        with TemporaryDirectory() as testdir:
            self.testfile = os.path.join(
                testdir, str(random.random()) + ".xlsx"
            )
            print(self.testfile)

            source = XLSXSource(
                XLSXSourceConfig(
                    filename=self.testfile, allowempty=True, readwrite=True,
                )
            )

            await save(
                source,
                Record("1", data={"features": {"A": 1, "B": 2}}),
                Record("2", data={"features": {"C": 3, "D": 4}}),
            )

            records = [record async for record in load(source)]

            self.assertIsInstance(records, list)
            self.assertEqual(len(records), 2)
            # None is expected behaviour because the columns are empty.
            self.assertDictEqual(
                records[0].features(), {"A": 1, "B": 2, "C": None, "D": None}
            )
            self.assertDictEqual(
                records[1].features(), {"A": None, "B": None, "C": 3, "D": 4}
            )
