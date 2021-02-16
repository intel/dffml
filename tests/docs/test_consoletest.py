import os
import sys
import inspect
import pathlib
import tempfile
import unittest
import contextlib
import dataclasses
import unittest.mock
import importlib.util

from dffml.util.asynctestcase import AsyncTestCase

from dffml.util.testing.consoletest.commands import *
from dffml.util.testing.consoletest.cli import main as consoletest_doc


ROOT_PATH = pathlib.Path(__file__).parent.parent.parent
DOCS_PATH = ROOT_PATH / "docs"


# Load files by path. We have to import literalinclude_diff for diff-files
for module_name in ["literalinclude_diff"]:
    spec = importlib.util.spec_from_file_location(
        module_name, str(ROOT_PATH / "docs" / "_ext" / f"{module_name}.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    setattr(sys.modules[__name__], module_name, module)


class TestDocs(AsyncTestCase):
    """
    A testcase for each doc will be added to this class
    """

    TESTABLE_DOCS = []

    def test__all_docs_being_tested(self):
        """
        Make sure that there is a jobs.tutorials.strategy.matrix.docs entry for
        each testable doc.
        """
        # Ensure that we identified some docs to test
        should_have = sorted(self.TESTABLE_DOCS)
        self.assertTrue(should_have)
        # Load the ci testing workflow avoid requiring the yaml module as that
        # has C dependencies
        docs = list(
            sorted(
                map(
                    lambda i: str(
                        pathlib.Path(ROOT_PATH, i.strip()[2:])
                        .relative_to(DOCS_PATH)
                        .with_suffix("")
                    ),
                    filter(
                        lambda line: line.strip().startswith("- docs/"),
                        pathlib.Path(
                            ROOT_PATH, ".github", "workflows", "testing.yml"
                        )
                        .read_text()
                        .split("\n"),
                    ),
                )
            )
        )
        # Make sure that we have an entry for all the docs we can test
        self.assertListEqual(should_have, docs)


def mktestcase(filepath: pathlib.Path, relative: pathlib.Path, builder: bool):
    async def testcase(self):
        return await consoletest_doc(
            [
                str(filepath.resolve()),
                "--root",
                str(ROOT_PATH),
                "--docs",
                str(DOCS_PATH),
            ]
        )

    def builder_testcase(self):
        from sphinx.cmd.build import (
            get_parser,
            Tee,
            color_terminal,
            patch_docutils,
            docutils_namespace,
            Sphinx,
        )
        from sphinx.environment import BuildEnvironment

        os.chdir(str(ROOT_PATH))

        filenames = [str(relative)]

        class SubSetBuildEnvironment(BuildEnvironment):
            def get_outdated_files(self, updated):
                added, changed, removed = super().get_outdated_files(updated)
                added.clear()
                changed.clear()
                removed.clear()
                added.add("index")
                for filename in filenames:
                    added.add(filename)
                return added, changed, removed

        class SubSetSphinx(Sphinx):
            def _init_env(self, freshenv: bool) -> None:
                self.env = SubSetBuildEnvironment()
                self.env.setup(self)
                self.env.find_files(self.config, self.builder)

        confdir = str(ROOT_PATH / "docs")

        pickled_objs = {}

        def pickle_dump(obj, fileobj, _protocol):
            pickled_objs[fileobj.name] = obj

        def pickle_load(fileobj):
            return pickled_objs[fileobj.name]

        with patch_docutils(
            confdir
        ), docutils_namespace(), unittest.mock.patch(
            "pickle.dump", new=pickle_dump
        ), unittest.mock.patch(
            "pickle.load", new=pickle_load
        ), tempfile.TemporaryDirectory() as tempdir:
            app = SubSetSphinx(
                str(ROOT_PATH / "docs"),
                confdir,
                os.path.join(tempdir, "consoletest"),
                os.path.join(tempdir, "consoletest", ".doctrees"),
                "consoletest",
                {},
                sys.stdout,
                sys.stderr,
                True,
                False,
                [],
                0,
                1,
                False,
            )
            app.build(False, [])
        self.assertFalse(app.statuscode)

    if builder:
        return builder_testcase
    return testcase


SKIP_DOCS = ["swportal", "plugins/dffml_model"]
# Quick examples with no install commands, no venv needed
NO_SETUP = [
    "tutorials/doublecontextentry",
]


for filepath in DOCS_PATH.rglob("*.rst"):
    if b":test:" not in pathlib.Path(filepath).read_bytes():
        continue
    relative = filepath.relative_to(DOCS_PATH).with_suffix("")
    if str(relative) in SKIP_DOCS:
        continue
    # Create the testcase
    testcase = mktestcase(filepath, relative, str(relative) not in NO_SETUP)
    if str(relative) not in NO_SETUP:
        # Don't check for a long test entry in the workflow if doc in NO_SETUP
        TestDocs.TESTABLE_DOCS.append(str(relative))
        # Skip if not in NO_SETUP and RUN_CONSOLETESTS not set
        testcase = unittest.skipIf(
            "RUN_CONSOLETESTS" not in os.environ,
            "RUN_CONSOLETESTS environment variable not set",
        )(testcase)
        # Do not add the tests if we are running with GitHub Actions for the main
        # package. This is because there are seperate jobs for each tutorial test
        # and the TestDocs.test__all_docs_being_tested ensures that we are running a
        # job for each tutorial
        if (
            "GITHUB_ACTIONS" in os.environ
            and "PLUGIN" in os.environ
            and os.environ["PLUGIN"] == "."
        ):
            continue
    # Add the testcase
    name = "test_" + str(relative).replace(os.sep, "_")
    setattr(TestDocs, name, testcase)
