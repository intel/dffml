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
    async def test_repos(self):
        keys = ["A", "B", "C"]
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "list",
                "repos",
                "-sources",
                "feed=memory",
                "-source-repos",
                *keys,
            )
        stdout = self.stdout.getvalue()
        for key in keys:
            self.assertIn(key, stdout)


class TestMerge(IntegrationCLITestCase):
    async def test_memory_to_json(self):
        keys = ["A", "B", "C"]
        filename = self.mktempfile()
        await CLI.cli(
            "merge",
            "dest=json",
            "src=memory",
            "-source-dest-filename",
            filename,
            "-source-src-repos",
            *keys,
            "-source-src-allowempty",
            "-source-dest-allowempty",
            "-source-src-readwrite",
            "-source-dest-readwrite",
        )
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "list",
                "repos",
                "-sources",
                "tmp=json",
                "-source-tmp-filename",
                filename,
            )
        stdout = self.stdout.getvalue()
        for key in keys:
            self.assertIn(key, stdout)

    async def test_memory_to_csv(self):
        keys = ["A", "B", "C"]
        filename = self.mktempfile()
        await CLI.cli(
            "merge",
            "dest=csv",
            "src=memory",
            "-source-dest-filename",
            filename,
            "-source-src-repos",
            *keys,
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
