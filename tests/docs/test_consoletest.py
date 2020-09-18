import os
import tempfile
import unittest
import contextlib
import importlib.util


# Root of DFFML source tree
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")

# Load file by path
spec = importlib.util.spec_from_file_location(
    "consoletest", os.path.join(ROOT_DIR, "docs", "_ext", "consoletest.py")
)
consoletest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consoletest)


class TestFunctions(unittest.TestCase):
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
            consoletest.VirtualEnvCommand(".venv"),
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

    def test_run_commands(self):
        with tempfile.TemporaryFile() as stdout:
            with contextlib.redirect_stdout(stdout):
                consoletest.run_commands(
                    [
                        ["python3", "-c", r"print('Hello\nWorld')"],
                        ["grep", "Hello", "2>&1"],
                    ],
                    {"cwd": os.getcwd()},
                )
            stdout.seek(0)
            stdout = stdout.read().decode().strip()
            self.assertEqual(stdout, "Hello")


class TestPipInstallCommand(unittest.TestCase):
    def test_fix_dffml_packages(self):
        self.assertListEqual(
            consoletest.PipInstallCommand.fix_dffml_packages(
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
            ),
            [
                "pip",
                "install",
                "-U",
                os.path.abspath(ROOT_DIR),
                "-e",
                os.path.abspath(os.path.join(ROOT_DIR, "model", "scikit")),
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
