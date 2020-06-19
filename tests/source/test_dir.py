import os
import pathlib
import tempfile
import inspect
import numpy as np
import contextlib

from dffml.source.dir import DirectorySource, DirectorySourceConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.os import chdir
from dffml.cli.cli import CLI
from dffml.source.source import Sources
from dffml.record import Record


class TestDirectorySource(AsyncTestCase):
    @contextlib.contextmanager
    def setUpDirectory(self):
        blank_image = np.zeros((100, 100, 3), dtype=np.uint8)
        with tempfile.TemporaryDirectory() as tempdir:
            with chdir(tempdir):
                for dirname in ["a", "b", "c"]:
                    dirpath = pathlib.Path(dirname)
                    if not os.path.exists(dirpath):
                        dirpath.mkdir()
                    for image_name in ["x", "y", "z"]:
                        # This is not saved in png file format so isn;t loaded by configloader
                        # Need to find a better way.
                        (dirpath / (image_name + ".png")).write_bytes(
                            bytearray(blank_image.flatten())
                        )
                yield tempdir

    def setUpSource(self):
        with self.setUpDirectory() as tempdir:
            return DirectorySource(
                DirectorySourceConfig(
                    foldername=".", feature="image", labels=["a", "b", "c"],
                )
            )

    async def test_dir(self):
        records = []
        async with self.setUpSource() as source:
            async with source() as sctx:
                async for record in sctx.records():
                    records.append(record)
                    self.assertEqual(
                        [*record.features().keys()],
                        [sctx.parent.config.feature, "label"],
                    )
                    self.assertIsInstance(
                        record.features()[sctx.parent.config.feature],
                        (list, tuple,),
                    )
                    self.assertIn(
                        record.features()["label"], sctx.parent.config.labels
                    )

                    self.assertEqual(
                        len(record.features()[sctx.parent.config.feature]),
                        28 * 28,
                    )

        self.assertEqual(len(records), 9)
