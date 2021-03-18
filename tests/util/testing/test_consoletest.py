import os
import sys
import inspect
import pathlib
import tempfile
import unittest
import platform
import contextlib
import unittest.mock
import importlib.util

from dffml.util.asynctestcase import AsyncTestCase

from dffml.util.testing.consoletest.commands import *
from dffml.util.testing.consoletest.parser import parse_nodes, Node
from dffml.util.testing.consoletest.runner import run_nodes
from dffml.util.testing.consoletest.util import nodes_to_test


# Root of DFFML source tree
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")
CONSOLETEST_README_PATH = pathlib.Path(
    ROOT_DIR, "dffml", "util", "testing", "consoletest", "README.md"
)


class TestFunctions(AsyncTestCase):
    def test_parse_commands_multi_line(self):
        self.assertListEqual(
            parse_commands(
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
                    parse_commands(cmd)

        cmd = ["$ python3 '`cat feedface`'"]
        with self.subTest(cmd=cmd):
            parse_commands(cmd)

    def test_parse_commands_single_line_with_output(self):
        self.assertListEqual(
            parse_commands(
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
            build_command([".", ".venv/bin/activate"],),
            ActivateVirtualEnvCommand(".venv"),
        )

    def test_pipes(self):
        self.assertListEqual(
            pipes(
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
            await run_commands(
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
        command = PipInstallCommand(
            [
                "python",
                "-m",
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
        command.fix_dffml_packages({"root": ROOT_DIR})
        self.assertListEqual(
            command.cmd,
            [
                "python",
                "-m",
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
            DockerRunCommand.find_name(
                ["docker", "run", "--rm", "-d", "--name", "maintained_db",]
            ),
            (
                "maintained_db",
                False,
                ["docker", "run", "--rm", "-d", "--name", "maintained_db",],
            ),
        )


class TestParser(unittest.TestCase):
    def test_parse_nodes(self):
        self.maxDiff = None
        self.assertListEqual(
            list(
                filter(
                    lambda node: node.directive
                    in {"code-block", "literalinclude"},
                    parse_nodes(
                        inspect.cleandoc(
                            r"""
                .. code-block:: console
                    :test:

                    $ echo -e 'Hello\n\n\nWorld'
                    Hello


                    World

                .. literalinclude:: some/file.py
                    :filepath: myfile.py
                    :test:

                .. note::

                    .. note::

                        .. code-block:: console
                            :test:
                            :daemon: 8080

                            $ echo -e 'Hello\n\n\n    World\n\n\nTest'
                            Hello


                                World


                            Test

                    .. code-block:: console

                        $ echo -e 'Hello\n\n\n    World\n\n\n\n'
                        Hello


                            World



                        $ echo 'feedface'
                        feedface

                    .. note::

                        .. code-block:: console
                            :test:

                            $ echo feedface
                            feedface

                .. code-block:: console
                    :test:

                    $ echo feedface
                    feedface
                """
                        )
                    ),
                )
            ),
            [
                Node(
                    directive="code-block",
                    content=[
                        r"$ echo -e 'Hello\n\n\nWorld'",
                        "Hello",
                        "",
                        "",
                        "World",
                    ],
                    options={"test": True},
                    node={},
                ),
                Node(
                    directive="literalinclude",
                    content="",
                    options={"filepath": "myfile.py", "test": True},
                    node={"source": "some/file.py"},
                ),
                Node(
                    directive="code-block",
                    content=[
                        r"$ echo -e 'Hello\n\n\n    World\n\n\nTest'",
                        "Hello",
                        "",
                        "",
                        "    World",
                        "",
                        "",
                        "Test",
                    ],
                    options={"test": True, "daemon": "8080"},
                    node={},
                ),
                Node(
                    directive="code-block",
                    content=[
                        r"$ echo -e 'Hello\n\n\n    World\n\n\n\n'",
                        "Hello",
                        "",
                        "",
                        "    World",
                        "",
                        "",
                        "",
                        "$ echo 'feedface'",
                        "feedface",
                    ],
                    options={},
                    node={},
                ),
                Node(
                    directive="code-block",
                    content=["$ echo feedface", "feedface",],
                    options={"test": True},
                    node={},
                ),
                Node(
                    directive="code-block",
                    content=["$ echo feedface", "feedface",],
                    options={"test": True},
                    node={},
                ),
            ],
        )


class TestRunner(AsyncTestCase):
    @unittest.skipUnless(platform.system() == "Linux", "Only runs on Linux")
    async def test_run_nodes(self):
        with contextlib.ExitStack() as stack:
            await run_nodes(
                CONSOLETEST_README_PATH.parent,
                CONSOLETEST_README_PATH.parent,
                stack,
                nodes_to_test(
                    parse_nodes(CONSOLETEST_README_PATH.read_text())
                ),
            )
