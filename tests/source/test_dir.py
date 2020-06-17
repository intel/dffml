import pathlib
import tempfile
import inspect

from dffml.source.dir import DirectorySource, DirectorySourceConfig
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.os import chdir
from dffml.cli.cli import CLI
from dffml.source.source import Sources
from dffml.record import Record


class TestDirectorySource(AsyncTestCase):
    def setUpSource(self):
        return DirectorySource(
            DirectorySourceConfig(
                foldername=pathlib.Path(__file__).parent / "dataset" / "train",
                feature="image",
                labels=["airplane", "bird", "frog"],
            )
        )

    async def test_dir(self):
        records_from_cli = await CLI.cli(
            "list",
            "records",
            "-sources",
            "f=dir",
            "-source-foldername",
            "tests/source/dataset/train",
            "-source-feature",
            "image",
            "-source-labels",
            "airplane",
            "bird",
            "frog",
        )

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

        self.assertDictEqual(records[0].export(), records_from_cli[0].export())
        self.assertEqual(len(records), 15)
        self.assertEqual(len(records_from_cli), 15)
