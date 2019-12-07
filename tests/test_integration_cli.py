"""
This file contains integration tests. We use the CLI to exercise functionality of
various DFFML classes and constructs.
"""
import re
import os
import io
import json
import inspect
import pathlib
import asyncio
import contextlib
import unittest.mock

from dffml.df.types import Operation, DataFlow
from dffml.cli.cli import CLI
from dffml.service.dev import Develop
from dffml.util.packaging import is_develop
from dffml.util.entrypoint import load
from dffml.util.asynctestcase import AsyncTestCase

from .test_cli import non_existant_tempfile


def relative_path(*args):
    """
    Returns a pathlib.Path object with the path relative to this file.
    """
    target = pathlib.Path(__file__).parents[0] / args[0]
    for path in list(args)[1:]:
        target /= path
    return target


@contextlib.contextmanager
def relative_chdir(*args):
    """
    Change directory to a location relative to the location of this file.
    """
    target = relative_path(*args)
    orig_dir = os.getcwd()
    try:
        os.chdir(target)
        yield target
    finally:
        os.chdir(orig_dir)


class IntegrationCLITestCase(AsyncTestCase):
    REQUIRED_PLUGINS = []

    async def setUp(self):
        super().setUp()
        self.required_plugins(*self.REQUIRED_PLUGINS)
        self.stdout = io.StringIO()
        self._stack = contextlib.ExitStack().__enter__()

    async def tearDown(self):
        super().tearDown()
        self._stack.__exit__(None, None, None)

    def required_plugins(self, *args):
        if not all(map(is_develop, args)):
            self.skipTest(
                f"Required plugins: {', '.join(args)} must be installed in development mode"
            )

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


class TestDevelop(IntegrationCLITestCase):
    async def test_export(self):
        self.required_plugins("shouldi")
        stdout = io.StringIO()
        # Use shouldi's dataflow for tests
        with relative_chdir("..", "examples", "shouldi"):
            with unittest.mock.patch("sys.stdout.buffer.write") as write:
                await Develop.cli("export", "shouldi.cli:DATAFLOW")
            DataFlow._fromdict(**json.loads(write.call_args[0][0]))

    async def test_run(self):
        self.required_plugins("shouldi", "dffml-model-scratch")
        results = await Develop.cli(
            "run",
            "-log",
            "debug",
            "shouldi.bandit:run_bandit",
            "-pkg",
            str(relative_path("..", "model", "scratch")),
        )
        self.assertIn("bandit_output", results)
        self.assertIn(
            "CONFIDENCE.HIGH_AND_SEVERITY.HIGH", results["bandit_output"]
        )


class TestDataFlow(IntegrationCLITestCase):

    REQUIRED_PLUGINS = ["shouldi", "dffml-config-yaml", "dffml-feature-git"]

    async def setUp(self):
        await super().setUp()
        # Use shouldi's dataflow for tests
        self.DATAFLOW = list(
            load(
                "shouldi.cli:DATAFLOW",
                relative=relative_path("..", "examples", "shouldi"),
            )
        )[0]

    async def test_diagram_default(self):
        filename = self.mktempfile() + ".json"
        pathlib.Path(filename).write_text(json.dumps(self.DATAFLOW.export()))
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "dataflow", "diagram", filename,
            )
        stdout = self.stdout.getvalue()
        # Check that a subgraph is being made for each operation
        self.assertTrue(re.findall(r"subgraph.*run_bandit", stdout))
        # Check that all stages are included
        for check in ["Processing", "Output", "Cleanup"]:
            self.assertIn(f"{check} Stage", stdout)

    async def test_diagram_simple(self):
        filename = self.mktempfile() + ".json"
        pathlib.Path(filename).write_text(json.dumps(self.DATAFLOW.export()))
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "dataflow", "diagram", "-simple", filename,
            )
        # Check that a subgraph is not being made for each operation
        self.assertFalse(
            re.findall(r"subgraph.*run_bandit", self.stdout.getvalue())
        )

    async def test_diagram_single_stage(self):
        filename = self.mktempfile() + ".json"
        pathlib.Path(filename).write_text(json.dumps(self.DATAFLOW.export()))
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "dataflow", "diagram", "-stages", "processing", "--", filename,
            )
        stdout = self.stdout.getvalue()
        # Check that the single stage is not its own subgraph
        for check in ["Processing", "Output", "Cleanup"]:
            self.assertNotIn(f"{check} Stage", stdout)

    async def test_diagram_multi_stage(self):
        filename = self.mktempfile() + ".json"
        pathlib.Path(filename).write_text(json.dumps(self.DATAFLOW.export()))
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "dataflow",
                "diagram",
                "-stages",
                "processing",
                "output",
                "--",
                filename,
            )
        stdout = self.stdout.getvalue()
        # Check that the single stage is not its own subgraph
        for check in ["Processing", "Output"]:
            self.assertIn(f"{check} Stage", stdout)
        for check in ["Cleanup"]:
            self.assertNotIn(f"{check} Stage", stdout)

    async def test_merge(self):
        # Write out shouldi dataflow
        orig = self.mktempfile() + ".json"
        pathlib.Path(orig).write_text(json.dumps(self.DATAFLOW.export()))
        # Import from feature/git
        transform_to_repo = Operation.load("dffml.mapping.create")
        lines_of_code_by_language, lines_of_code_to_comments = list(
            load(
                "dffml_feature_git.feature.operations:lines_of_code_by_language",
                "dffml_feature_git.feature.operations:lines_of_code_to_comments",
                relative=relative_path("..", "feature", "git"),
            )
        )
        # Create new dataflow
        override = DataFlow.auto(
            transform_to_repo,
            lines_of_code_by_language,
            lines_of_code_to_comments,
        )
        # TODO Modify and compare against yaml in docs example
        # Write out override dataflow
        created = self.mktempfile() + ".json"
        pathlib.Path(created).write_text(json.dumps(override.export()))
        # Merge the two
        with contextlib.redirect_stdout(self.stdout):
            await CLI.cli(
                "dataflow", "merge", orig, created,
            )
        DataFlow._fromdict(**json.loads(self.stdout.getvalue()))
