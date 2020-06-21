import os
import pathlib
import tempfile
import contextlib

from PIL import Image
import numpy as np

from dffml.source.dir import DirectorySource, DirectorySourceConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.os import chdir


class TestDirectorySource(AsyncTestCase):
    @contextlib.contextmanager
    def setUpDirectory(self):
        blank_image = Image.new(mode="RGB", size=(50, 50))
        with tempfile.TemporaryDirectory() as tempdir:
            with chdir(tempdir):
                for dirname in ["a", "b", "c"]:
                    dirpath = pathlib.Path(dirname)
                    if not os.path.exists(dirpath):
                        dirpath.mkdir()
                    for image_name in ["x", "y", "z"]:
                        blank_image.save(dirpath / (image_name + ".png"))
                yield tempdir

    def setUpSource(self):
        return DirectorySource(
            DirectorySourceConfig(
                foldername=os.getcwd(),
                feature="image",
                labels=["a", "b", "c"],
            )
        )

    async def test_dir(self):
        records = []
        with self.setUpDirectory() as tempdir:
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
                            (list, tuple, np.ndarray),
                        )
                        self.assertIn(
                            record.features()["label"],
                            sctx.parent.config.labels,
                        )

                        self.assertEqual(
                            len(record.features()[sctx.parent.config.feature]),
                            50 * 50 * 3,
                        )

        self.assertEqual(len(records), 9)
