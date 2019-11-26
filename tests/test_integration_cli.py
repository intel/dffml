"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import io
import inspect
import pathlib
import contextlib

from dffml.cli.cli import CLI
from dffml.util.asynctestcase import AsyncTestCase

from .test_cli import non_existant_tempfile


class IntegrationCLITestCase(AsyncTestCase):
    async def setUp(self):
        super().setUp()
        self.stdout = io.StringIO()
        self._stack = contextlib.ExitStack().__enter__()

    async def tearDown(self):
        super().tearDown()
        self._stack.__exit__(None, None, None)

    def mktempfile(self):
        return self._stack.enter_context(non_existant_tempfile())


class TestList(IntegrationCLITestCase):
    async def test_repos(self):
        src_urls = ["A", "B", "C"]
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "list",
                "repos",
                "-sources",
                "feed=memory",
                "-source-repos",
                *src_urls,
            )
        stdout = self.stdout.getvalue()
        for src_url in src_urls:
            self.assertIn(src_url, stdout)


class TestMerge(IntegrationCLITestCase):
    async def test_memory_to_json(self):
        src_urls = ["A", "B", "C"]
        filename = self.mktempfile()
        await CLI.cli(
            "merge",
            "dest=json",
            "src=memory",
            "-source-dest-filename",
            filename,
            "-source-src-repos",
            *src_urls,
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
        for src_url in src_urls:
            self.assertIn(src_url, stdout)

    async def test_memory_to_csv(self):
        src_urls = ["A", "B", "C"]
        filename = self.mktempfile()
        await CLI.cli(
            "merge",
            "dest=csv",
            "src=memory",
            "-source-dest-filename",
            filename,
            "-source-src-repos",
            *src_urls,
        )
        self.assertEqual(
            pathlib.Path(filename).read_text(),
            inspect.cleandoc(
                """
                src_url,label,prediction,confidence
                A,unlabeled,,
                B,unlabeled,,
                C,unlabeled,,
                """
            )
            + "\n",
        )
