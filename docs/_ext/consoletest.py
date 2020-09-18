"""
Used to test ``code-block:: console`` portions of Sphinx documentation.
"""
import os
import abc
import sys
import time
import copy
import shlex
import signal
import atexit
import shutil
import tempfile
import contextlib
import subprocess
import importlib.util
from typing import (
    Any,
    Dict,
    List,
    Union,
)

from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import directives

import sphinx
from sphinx.directives.code import LiteralInclude
from sphinx.locale import __
from sphinx.ext.doctest import DocTestBuilder
from sphinx.util.docutils import SphinxDirective


# Root of DFFML source tree
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")

# Load file by path
spec = importlib.util.spec_from_file_location(
    "plugins", os.path.join(ROOT_DIR, "dffml", "plugins.py")
)
plugins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugins)


class ConsoletestCommand(abc.ABC):
    def __init__(self):
        self.poll_until = None
        self.ignore_errors = False
        self.daemon = False

    def __repr__(self):
        return (
            self.__class__.__qualname__
            + "("
            + str(
                {
                    k: v
                    for k, v in self.__dict__.items()
                    if not k.startswith("_")
                }
            )
            + ")"
        )

    def str(self):
        return repr(self)

    def __enter__(self):
        pass

    def __exit__(self, _exc_type, _exc_value, _traceback):
        pass


class VirtualEnvCommand(ConsoletestCommand):
    def __init__(self, directory: str):
        super().__init__()
        self.directory = directory
        self.old_virtual_env = None
        self.old_path = None

    def __eq__(self, other: "VirtualEnvCommand"):
        return bool(
            hasattr(other, "directory") and self.directory == other.directory
        )

    def run(self, ctx):
        self.old_virtual_env = os.environ.get("VIRTUAL_ENV", None)
        self.old_path = os.environ.get("PATH", None)
        os.environ["VIRTUAL_ENV"] = os.path.abspath(
            os.path.join(ctx["cwd"], self.directory)
        )
        os.environ["PATH"] = ":".join(
            [os.path.abspath(os.path.join(ctx["cwd"], self.directory, "bin"))]
            + os.environ.get("PATH", "").split(":")
        )

    def __exit__(self, _exc_type, _exc_value, _traceback):
        if self.old_virtual_env is not None:
            os.environ["VIRTUAL_ENV"] = self.old_virtual_env
        if self.old_path is not None:
            os.environ["PATH"] = self.old_path


def run_commands(
    cmds,
    ctx,
    *,
    stdout: Union[str, bytes] = None,
    ignore_errors: bool = False,
    daemon: bool = False,
):
    proc = None
    procs = []
    for i, cmd in enumerate(map(sub_env_vars, cmds)):
        kwargs = {}
        # Set stdout to system stdout so it doesn't go to the pty
        kwargs["stdout"] = stdout if stdout is not None else sys.stdout
        # Check if there is a previous command
        if i != 0:
            kwargs["stdin"] = proc.stdout
        # Check if there is a next command
        if i + 1 < len(cmds):
            kwargs["stdout"] = subprocess.PIPE
        # Check if we redirect stderr to stdout
        if "2>&1" in cmd:
            kwargs["stderr"] = subprocess.STDOUT
            cmd.remove("2>&1")
        # If not in venv ensure correct Python
        if not "VIRTUAL_ENV" in os.environ and cmd[0].startswith("python"):
            cmd[0] = sys.executable
        # Run the command
        proc = subprocess.Popen(
            cmd, start_new_session=True, cwd=ctx["cwd"], **kwargs
        )
        proc.cmd = cmd
        procs.append(proc)
        # Parent (this Python process) close stdout of previous command so that
        # the command we just created has exclusive access to the output.
        if i != 0:
            kwargs["stdin"].close()
    # Wait for all processes to complete
    errors = []
    for i, proc in enumerate(procs):
        # Do not wait for last process to complete if running in daemon mode
        if daemon and (i + 1) == len(procs):
            break
        proc.wait()
        if proc.returncode != 0:
            errors.append(f"Failed to run: {cmd!r}")
    if errors and not ignore_errors:
        raise RuntimeError("\n".join(errors))
    if daemon:
        return procs[-1]


def sub_env_vars(cmd):
    for env_var_name, env_var_value in os.environ.items():
        for i, arg in enumerate(cmd):
            for check in ["$" + env_var_name, "${" + env_var_name + "}"]:
                if check in arg:
                    cmd[i] = arg.replace(check, env_var_value)
    return cmd


def pipes(cmd):
    if not "|" in cmd:
        return [cmd]
    cmds = []
    j = 0
    for i, arg in enumerate(cmd):
        if arg == "|":
            cmds.append(cmd[j:i])
            j = i + 1
    cmds.append(cmd[j:])
    return cmds


class ConsoleCommand(ConsoletestCommand):
    def __init__(self, cmd: List[str]):
        super().__init__()
        self.cmd = cmd
        self.daemon_proc = None

    def run(self, ctx):
        if self.poll_until is None:
            self.daemon_proc = run_commands(
                pipes(self.cmd),
                ctx,
                ignore_errors=self.ignore_errors,
                daemon=self.daemon,
            )
        else:
            while True:
                with tempfile.TemporaryFile() as stdout:
                    run_commands(
                        pipes(self.cmd),
                        ctx,
                        stdout=stdout,
                        ignore_errors=self.ignore_errors,
                    )
                    stdout.seek(0)
                    stdout = stdout.read().decode()
                    if call_poll_until(self.poll_until, stdout):
                        return
                time.sleep(0.1)

    def __exit__(self, _exc_type, _exc_value, _traceback):
        # Send ctrl-c to daemon if running
        if self.daemon_proc is not None:
            self.daemon_proc.send_signal(signal.SIGINT)
            self.daemon_proc.wait()


class PipInstallCommand(ConsoleCommand):
    def __init__(self, cmd: List[str]):
        super().__init__(self.fix_dffml_packages(cmd))

    @staticmethod
    def fix_dffml_packages(cmd):
        """
        If a piece of the documentation says to install dffml or one of the
        packages, we need to make sure that the version from the current branch
        gets installed instead, since we don't want to test the released
        version, we want to test the version of the codebase as it is.
        """
        package_names_to_directory = copy.copy(
            plugins.PACKAGE_NAMES_TO_DIRECTORY
        )
        package_names_to_directory["dffml"] = "."
        for i, pkg in enumerate(cmd):
            if pkg in package_names_to_directory:
                directory = package_names_to_directory[pkg]
                directory = os.path.join(ROOT_DIR, *directory)
                directory = os.path.abspath(directory)
                cmd[i] = directory
        return cmd


class DockerRunCommand(ConsoleCommand):
    def __init__(self, cmd: List[str]):
        name, needs_removal, cmd = self.find_name(cmd)
        super().__init__(cmd)
        self.name = name
        self.needs_removal = needs_removal
        self.stopped = False

    @staticmethod
    def find_name(cmd):
        """
        Find the name of the container we are starting (if starting as daemon)
        """
        name = None
        needs_removal = bool("--rm" not in cmd)
        for i, arg in enumerate(cmd):
            if arg.startswith("--name="):
                name = arg[len("--name=") :]
            elif arg == "--name" and (i + 1) < len(cmd):
                name = cmd[i + 1]
        return name, needs_removal, cmd

    def cleanup(self):
        if self.name and not self.stopped:
            subprocess.check_call(["docker", "stop", self.name])
            if self.needs_removal:
                subprocess.check_call(["docker", "rm", self.name])
        self.stopped = True

    def __enter__(self):
        atexit.register(self.cleanup)

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.cleanup()


def within_qoute(current, qoute=('"', "'")):
    within = False
    for i, char in enumerate(current):
        context = current[i - 1 : i]
        if char in qoute and not context.startswith("\\"):
            within = not within
    return within


def parse_commands(content):
    commands = []

    current = ""
    for line in content:
        line = line.rstrip()
        if line.startswith("$ "):
            if line.endswith("\\"):
                current = line[2:-1]
            else:
                current = line[2:]
                if within_qoute(current):
                    continue
                commands.append(current)
                current = ""
        elif current and line.endswith("\\"):
            current += line[:-1]
        elif current and not line.endswith("\\"):
            current += line
            if within_qoute(current):
                continue
            commands.append(current)
            current = ""

    # Raise NotImplementedError if command substitution is attempted
    for command in commands:
        for check in ("`", "$("):
            index = 0
            while index != -1:
                index = command.find(check, index + 1)
                if index == -1:
                    continue
                if not within_qoute(command[:index], qoute=("'")):
                    raise NotImplementedError(
                        f"Command substitution was attempted: {command}"
                    )

    try:
        commands = list(map(shlex.split, commands))
    except ValueError as error:
        print(commands)
        raise

    return commands


def build_command(cmd):
    if not cmd:
        raise ValueError("Empty command")
    # Handle virtualenv activation
    if ".\\.venv\\Scripts\\activate" in cmd or (
        len(cmd) == 2
        and cmd[0] in ("source", ".")
        and ".venv/bin/activate" == cmd[1]
    ):
        return VirtualEnvCommand(".venv")
    # TODO Handle cd
    # Handle pip installs
    if (
        "pip" in cmd
        and "install" in cmd
        and cmd[cmd.index("pip") + 1] == "install"
    ):
        return PipInstallCommand(cmd)
    # Handle docker commands
    if cmd[:2] == ["docker", "run"]:
        return DockerRunCommand(cmd)
    # Regular console command
    return ConsoleCommand(cmd)


# set up the necessary directives

MAKE_POLL_UNTIL_TEMPLATE = """
import sys

func = lambda stdout: {func}

sys.exit(int(not func(sys.stdin.buffer.read())))
"""


def call_poll_until(func, stdout):
    with tempfile.NamedTemporaryFile() as fileobj, tempfile.NamedTemporaryFile() as stdin:
        fileobj.write(MAKE_POLL_UNTIL_TEMPLATE.format(func=func).encode())
        fileobj.seek(0)
        stdin.write(stdout.encode() if isinstance(stdout, str) else stdout)
        stdin.seek(0)
        return_code = subprocess.call(["python", fileobj.name], stdin=stdin)
        return bool(return_code == 0)


class ConsoletestLiteralIncludeDirective(LiteralInclude):
    def run(self) -> List[Node]:
        retnodes = super().run()
        retnodes[0]["consoletest-literalinclude"] = True
        retnodes[0]["filepath"] = self.options.get(
            "filepath", os.path.basename(retnodes[0]["source"])
        ).split("/")
        return retnodes


ConsoletestLiteralIncludeDirective.option_spec.update(
    {"filepath": directives.unchanged_required,}
)


class ConsoletestDirective(SphinxDirective):
    option_spec = {
        "poll-until": directives.unchanged_required,
        "ignore-errors": directives.flag,
        "daemon": directives.flag,
    }

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self) -> List[Node]:
        code = "\n".join(self.content)
        nodetype = nodes.literal_block  # type: Type[TextElement]
        node = nodetype(
            code,
            code,
            language="console",
            consoletestnodetype=self.name,
            consoletest_commands=list(
                map(build_command, parse_commands(self.content))
            ),
        )
        self.set_source_info(node)

        poll_until = self.options.get("poll-until", None)
        ignore_errors = bool("ignore-errors" in self.options)
        for command in node["consoletest_commands"]:
            command.poll_until = poll_until
            command.ignore_errors = ignore_errors

        # Last command to be run is a daemon
        daemon = bool("daemon" in self.options)
        if daemon:
            node["consoletest_commands"][-1].daemon = True

        return [node]


class ConsoleTestBuilder(DocTestBuilder):
    name = "consoletest"
    epilog = __(
        "Testing of consoletests in the sources finished, look at the "
        "results in %(outdir)s/output.txt."
    )

    def init(self) -> None:
        self.total_failures = 0
        self.total_tries = 0

        date = time.strftime("%Y-%m-%d %H:%M:%S")

        self.outfile = open(
            os.path.join(self.outdir, "output.txt"), "w", encoding="utf-8"
        )
        self.outfile.write(
            (
                "Results of %s builder run on %s\n"
                "===========%s================%s\n"
            )
            % (self.name, date, "=" * len(self.name), "=" * len(date))
        )

    def finish(self) -> None:
        # write executive summary
        def s(v: int) -> str:
            return "s" if v != 1 else ""

        repl = (
            self.total_tries,
            s(self.total_tries),
            self.total_failures,
            s(self.total_failures),
        )
        self._out(
            f"""
{self.name} summary
{"=" * len(self.name)}========
%5d test%s
%5d failure%s in tests
"""
            % repl
        )
        self.outfile.close()

        if self.total_failures:
            self.app.statuscode = 1

    @staticmethod
    def condition(node: Node) -> bool:
        return isinstance(node, (nodes.literal_block, nodes.comment)) and (
            "consoletest_commands" in node
            or "consoletest-literalinclude" in node
        )

    def test_doc(self, docname: str, doctree: Node) -> None:
        # Get all applicable nodes
        doc_nodes = list(doctree.traverse(self.condition))

        if not doc_nodes:
            return

        print()
        print(f"{self.name} testing: {docname}")
        print()

        self.total_tries += 1

        try:
            with tempfile.TemporaryDirectory() as tempdir, contextlib.ExitStack() as stack:
                ctx = {"cwd": tempdir}

                for node in doc_nodes:  # type: Element
                    filename = self.get_filename_for_node(node, docname)
                    line_number = self.get_line_number(node)

                    if "consoletest-literalinclude" in node:
                        print()
                        print("Copying", node["source"], node["filepath"])
                        print()
                        shutil.copyfile(
                            node["source"],
                            os.path.join(ctx["cwd"], *node["filepath"]),
                        )
                    elif "consoletest_commands" in node:
                        for command in node["consoletest_commands"]:
                            print()
                            print("Running", command)
                            print()
                            stack.enter_context(command)
                            command.run(ctx)
                print()
                print("No more tempdir")
                print()
        except:
            self.total_failures += 1


def setup(app: "Sphinx") -> Dict[str, Any]:
    app.add_directive("consoletest", ConsoletestDirective)
    app.add_directive(
        "consoletest-literalinclude", ConsoletestLiteralIncludeDirective
    )
    app.add_builder(ConsoleTestBuilder)
    return {"version": "0.0.1", "parallel_read_safe": True}
