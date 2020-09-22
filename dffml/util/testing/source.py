# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import abc
import random
import tempfile

from ...record import Record, RecordPrediction
from ..asynctestcase import AsyncTestCase


class SourceTest(abc.ABC):
    """
    Test case class used to test a Source implementation. Subclass from and
    implement the setUpSource method.
    """

    @abc.abstractmethod
    async def setUpSource(self):
        pass  # pragma: no cover

    async def test_update(self):
        full_key = "0"
        empty_key = "1"
        full_record = Record(
            full_key,
            data={
                "features": {
                    "PetalLength": 3.9,
                    "PetalWidth": 1.2,
                    "SepalLength": 5.8,
                    "SepalWidth": 2.7,
                },
                "prediction": {
                    "target_name": RecordPrediction(
                        value="feedface", confidence=0.42
                    )
                },
            },
        )
        empty_record = Record(
            empty_key,
            data={
                "features": {
                    "PetalLength": 3.9,
                    "PetalWidth": 1.2,
                    "SepalLength": 5.8,
                    "SepalWidth": 2.7,
                }
            },
        )

        source = await self.setUpSource()
        async with source as testSource:
            # Open, update, and close
            async with testSource() as sourceContext:
                await sourceContext.update(full_record)
                await sourceContext.update(empty_record)
        async with source as testSource:
            # Open and confirm we saved and loaded correctly
            async with testSource() as sourceContext:
                with self.subTest(key=full_key):
                    record = await sourceContext.record(full_key)
                    self.assertEqual(
                        record.data.prediction["target_name"]["value"],
                        "feedface",
                    )
                    self.assertEqual(
                        record.data.prediction["target_name"]["confidence"],
                        0.42,
                    )
                with self.subTest(key=empty_key):
                    record = await sourceContext.record(empty_key)
                    self.assertEqual(
                        [
                            val["value"]
                            for _, val in record.data.prediction.items()
                        ],
                        [None] * (len(record.data.prediction)),
                    )
                with self.subTest(both=[full_key, empty_key]):
                    records = {
                        record.key: record
                        async for record in sourceContext.records()
                    }
                    self.assertIn(full_key, records)
                    self.assertIn(empty_key, records)

                    self.assertEqual(
                        records[full_key].features(), full_record.features()
                    )
                    self.assertEqual(
                        records[empty_key].features(), empty_record.features()
                    )


class FileSourceTest(SourceTest):
    """
    Test case class used to test a FileSource implementation.
    """

    async def test_update(self):
        with tempfile.TemporaryDirectory() as testdir:
            with self.subTest(extension=None):
                self.testfile = os.path.join(testdir, str(random.random()))
                await super().test_update()
            for extension in ["xz", "gz", "bz2", "lzma", "zip"]:
                with self.subTest(extension=extension):
                    self.testfile = os.path.join(
                        testdir, str(random.random()) + "." + extension
                    )
                    await super().test_update()

    async def test_tag(self):
        with tempfile.TemporaryDirectory() as testdir:
            self.testfile = os.path.join(testdir, str(random.random()))
            untagged = await self.setUpSource()
            tagged = await self.setUpSource()
            tagged.config = tagged.config._replace(tag="sometag")
            async with untagged, tagged:
                async with untagged() as uctx, tagged() as lctx:
                    await uctx.update(
                        Record("0", data={"features": {"feed": 1}})
                    )
                    await lctx.update(
                        Record("0", data={"features": {"face": 2}})
                    )
            async with untagged, tagged:
                async with untagged() as uctx, tagged() as lctx:
                    record = await uctx.record("0")
                    self.assertIn("feed", record.features())
                    record = await lctx.record("0")
                    self.assertIn("face", record.features())
