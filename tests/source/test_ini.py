import os
import tempfile

from dffml.record import Record
from dffml.high_level import load, save
from dffml.util.asynctestcase import AsyncTestCase
from dffml.source.ini import INISource, INISourceConfig


class TestINISource(AsyncTestCase):
    async def test_load_fd(self):
        # Test the loading function
        with tempfile.TemporaryDirectory() as testdir:
            # Create a source
            source = INISource(
                filename=os.path.join(testdir, "testfile.ini"),
                allowempty=True,
                readwrite=True,
            )
            # Save some data in the source
            await save(
                source,
                Record("section1", data={"features": {"A": 1, "B": 2,}}),
                Record("section2", data={"features": {"C": 3, "D": 4,}}),
            )
            # Load the data
            source.load("ini")

            # Test whether the data is loaded as expected or not
            self.assertIsInstance(source.mem, dict)
            self.assertIsInstance(source.mem["section1"], Record)
            self.assertDictEqual(
                source.mem["section1"].features(), {"A": 1, "B": 2,}
            )
            self.assertDictEqual(
                source.mem["section2"].features(), {"C": 3, "D": 4,}
            )

    async def test_dump_fd(self):
        with tempfile.TemporaryDirectory() as testdir:
            self.testfile = os.path.join(testdir, "testfile.ini")
            source = INISource(
                filename=self.testfile, allowempty=True, readwrite=True,
            )
            dump_data = {
                "section1": Record(
                    "section1", data={"features": {"A": 1, "B": 2,}}
                ),
                "section2": Record(
                    "section2", data={"features": {"C": 3, "D": 4,}}
                ),
            }
            source.mem = dump_data
            with open(self.testfile, "w") as tfile:
                await source.dump_fd(tfile)

            allrecords = [record async for record in load(source)]
            print(allrecords)
