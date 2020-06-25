"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import inspect
import pathlib
import contextlib

from dffml.cli.cli import CLI
from dffml.util.asynctestcase import IntegrationCLITestCase


class TestList(IntegrationCLITestCase):
    async def test_records(self):
        keys = ["A", "B", "C"]
        records = await CLI.cli(
            "list",
            "records",
            "-sources",
            "feed=memory",
            "-source-records",
            *keys,
        )
        records = list(map(lambda r: r.export(), records))
        records = dict(map(lambda r: (r["key"], r), records))
        for key in keys:
            self.assertIn(key, records)


class TestMerge(IntegrationCLITestCase):
    async def test_memory_to_json(self):
        keys = ["A", "B", "C"]
        filename = self.mktempfile()
        await CLI.cli(
            "merge",
            "src=memory",
            "dest=json",
            "-source-src-records",
            *keys,
            "-source-dest-filename",
            filename,
            "-source-src-allowempty",
            "-source-dest-allowempty",
            "-source-src-readwrite",
            "-source-dest-readwrite",
        )
        records = await CLI.cli(
            "list",
            "records",
            "-sources",
            "tmp=json",
            "-source-tmp-filename",
            filename,
        )
        records = list(map(lambda r: r.export(), records))
        records = dict(map(lambda r: (r["key"], r), records))
        for key in keys:
            self.assertIn(key, records)

    async def test_memory_to_csv(self):
        keys = ["A", "B", "C"]
        filename = self.mktempfile()
        await CLI.cli(
            "merge",
            "src=memory",
            "dest=csv",
            "-source-src-records",
            *keys,
            "-source-dest-filename",
            filename,
            "-source-src-allowempty",
            "-source-dest-allowempty",
            "-source-src-readwrite",
            "-source-dest-readwrite",
        )
        self.assertEqual(
            pathlib.Path(filename).read_text(),
            inspect.cleandoc(
                """
                key,tag
                A,untagged
                B,untagged
                C,untagged
                """
            )
            + "\n",
        )
