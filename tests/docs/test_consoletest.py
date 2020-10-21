import os
import sys
import pathlib
import tempfile
import unittest
import contextlib
import unittest.mock
import importlib.util

from dffml.util.asynctestcase import AsyncTestCase


# Root of DFFML source tree
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")

# Load files by path. We have to import literalinclude_diff for diff-files
for module_name in ["consoletest", "literalinclude_diff"]:
    spec = importlib.util.spec_from_file_location(
        module_name,
        os.path.join(ROOT_DIR, "docs", "_ext", f"{module_name}.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    setattr(sys.modules[__name__], module_name, module)


class TestFunctions(AsyncTestCase):
    def test_parse_commands_multi_line(self):
        self.assertListEqual(
            consoletest.parse_commands(
                [
                    "$ python3 -m \\",
                    "    venv \\",
                    "    .venv",
                    "some shit",
                    "",
                    "",
                    "$ . \\",
                    "    .venv/bin/activate",
                    "more asdflkj",
                    "",
                ]
            ),
            [["python3", "-m", "venv", ".venv"], [".", ".venv/bin/activate"],],
        )

    def test_parse_commands_substitution(self):
        for cmd in [
            ["$ python3 $(cat feedface)"],
            ["$ python3 `cat feedface`"],
            ['$ python3 "`cat feedface`"'],
        ]:
            with self.subTest(cmd=cmd):
                with self.assertRaises(NotImplementedError):
                    consoletest.parse_commands(cmd)

        cmd = ["$ python3 '`cat feedface`'"]
        with self.subTest(cmd=cmd):
            consoletest.parse_commands(cmd)

    def test_parse_commands_single_line_with_output(self):
        self.assertListEqual(
            consoletest.parse_commands(
                [
                    "$ docker logs maintained_db 2>&1 | grep 'ready for'",
                    "2020-01-13 21:31:09 0 [Note] mysqld: ready for connections.",
                    "2020-01-13 21:32:16 0 [Note] mysqld: ready for connections.",
                ]
            ),
            [
                [
                    "docker",
                    "logs",
                    "maintained_db",
                    "2>&1",
                    "|",
                    "grep",
                    "ready for",
                ],
            ],
        )

    def test_build_command_venv_linux(self):
        self.assertEqual(
            consoletest.build_command([".", ".venv/bin/activate"],),
            consoletest.ActivateVirtualEnvCommand(".venv"),
        )

    def test_pipes(self):
        self.assertListEqual(
            consoletest.pipes(
                [
                    "python3",
                    "-c",
                    r"print('Hello\nWorld')",
                    "|",
                    "grep",
                    "Hello",
                ]
            ),
            [["python3", "-c", r"print('Hello\nWorld')"], ["grep", "Hello"]],
        )

    async def test_run_commands(self):
        with tempfile.TemporaryFile() as stdout:
            await consoletest.run_commands(
                [
                    ["python3", "-c", r"print('Hello\nWorld')"],
                    ["grep", "Hello", "2>&1"],
                ],
                {"cwd": os.getcwd()},
                stdout=stdout,
            )
            stdout.seek(0)
            stdout = stdout.read().decode().strip()
            self.assertEqual(stdout, "Hello")


class TestPipInstallCommand(unittest.TestCase):
    def test_fix_dffml_packages(self):
        command = consoletest.PipInstallCommand(
            [
                "pip",
                "install",
                "-U",
                "dffml",
                "-e",
                "dffml-model-scikit",
                "shouldi",
                "aiohttp",
            ]
        )
        command.fix_dffml_packages()
        self.assertListEqual(
            command.cmd,
            [
                "pip",
                "install",
                "-U",
                "-e",
                os.path.abspath(ROOT_DIR),
                "-e",
                os.path.abspath(os.path.join(ROOT_DIR, "model", "scikit")),
                "-e",
                os.path.abspath(os.path.join(ROOT_DIR, "examples", "shouldi")),
                "aiohttp",
            ],
        )


class TestDockerRunCommand(unittest.TestCase):
    def test_find_name(self):
        self.assertEqual(
            consoletest.DockerRunCommand.find_name(
                ["docker", "run", "--rm", "-d", "--name", "maintained_db",]
            ),
            (
                "maintained_db",
                False,
                ["docker", "run", "--rm", "-d", "--name", "maintained_db",],
            ),
        )


class TestDocs(unittest.TestCase):
    """
    A testcase for each doc will be added to this class
    """


ROOT_PATH = pathlib.Path(__file__).parent.parent.parent
DOCS_PATH = ROOT_PATH / "docs"


def mktestcase(filepath: pathlib.Path, relative: pathlib.Path):
    # The test case itself, assigned to test_doctest of each class
    def testcase(self):
        from sphinx.cmd.build import (
            get_parser,
            Tee,
            color_terminal,
            patch_docutils,
            docutils_namespace,
            Sphinx,
        )
        from sphinx.environment import BuildEnvironment

        os.chdir(ROOT_DIR)

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

        confdir = os.path.join(ROOT_DIR, "docs")

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
                os.path.join(ROOT_DIR, "docs"),
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

    return testcase


for filepath in DOCS_PATH.rglob("*.rst"):
    if ":test:" not in pathlib.Path(filepath).read_text():
        continue
    relative = filepath.relative_to(DOCS_PATH).with_suffix("")
    name = "test_" + str(relative).replace(os.sep, "_")
    setattr(
        TestDocs,
        name,
        unittest.skipIf(
            "RUN_CONSOLETESTS" not in os.environ,
            "RUN_CONSOLETESTS environment variable not set",
        )(mktestcase(filepath, relative)),
    )
