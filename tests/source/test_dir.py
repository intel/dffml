import os
import pathlib
import tempfile
import contextlib

from PIL import Image

from dffml.source.dir import DirectorySource, DirectorySourceConfig
from dffml.util.asynctestcase import IntegrationCLITestCase
from dffml.util.os import chdir


class TestDirectorySource(IntegrationCLITestCase):

    REQUIRED_PLUGINS = ["dffml-config-image"]
    blank_image = Image.new(mode="RGB", size=(10, 10))

    @contextlib.contextmanager
    def setUpLabelledDirectory(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with chdir(tempdir):
                for dirname in ["a", "b", "c"]:
                    dirpath = pathlib.Path(dirname)
                    if not os.path.exists(dirpath):
                        dirpath.mkdir()
                    for image_name in ["x", "y", "z"]:
                        self.blank_image.save(dirpath / (image_name + ".png"))
                yield tempdir

    @contextlib.contextmanager
    def setUpUnlabelledDirectory(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with chdir(tempdir):
                for image_name in ["l", "m", "n", "o", "k"]:
                    self.blank_image.save(image_name + ".png")
                yield tempdir

    def setUpLabelledSource(self):
        return DirectorySource(
            DirectorySourceConfig(
                foldername=os.getcwd(),
                feature="image",
                labels=["a", "b", "c"],
            )
        )

    def setUpUnlabelledSource(self):
        return DirectorySource(
            DirectorySourceConfig(foldername=os.getcwd(), feature="image",)
        )

    async def test_dir_labelled(self):
        records = []
        with self.setUpLabelledDirectory() as tempdir:
            async with self.setUpLabelledSource() as source:
                async with source() as sctx:
                    async for record in sctx.records():
                        records.append(record)
                        self.assertEqual(
                            [*record.features().keys()],
                            [sctx.parent.config.feature, "label"],
                        )
                        self.assertIn(
                            record.features()[
                                sctx.parent.config.feature
                            ].__class__.__qualname__,
                            ("list", "tuple", "ndarray"),
                        )
                        self.assertIn(
                            record.features()["label"],
                            sctx.parent.config.labels,
                        )
                        self.assertEqual(
                            record.features()[
                                sctx.parent.config.feature
                            ].shape,
                            (10, 10, 3),
                        )

        self.assertEqual(len(records), 9)

    async def test_dir_unlabelled(self):
        records = []
        with self.setUpUnlabelledDirectory() as tempdir:
            async with self.setUpUnlabelledSource() as source:
                async with source() as sctx:
                    async for record in sctx.records():
                        records.append(record)
                        self.assertEqual(
                            [*record.features().keys()],
                            [sctx.parent.config.feature],
                        )
                        self.assertIn(
                            record.features()[
                                sctx.parent.config.feature
                            ].__class__.__qualname__,
                            ("list", "tuple", "ndarray"),
                        )
                        self.assertEqual(
                            record.features()[
                                sctx.parent.config.feature
                            ].shape,
                            (10, 10, 3),
                        )

        self.assertEqual(len(records), 5)
