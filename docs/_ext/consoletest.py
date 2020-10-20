"""
Used to test ``code-block:: console`` portions of Sphinx documentation.
"""
import os
import io
import abc
import sys
import json
import time
import copy
import shlex
import signal
import atexit
import shutil
import asyncio
import pathlib
import tempfile
import functools
import traceback
import threading
import contextlib
import subprocess
import importlib.util
from typing import (
    IO,
    Any,
    Dict,
    List,
    Union,
    Tuple,
    Optional,
)

from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import directives

import sphinx
from sphinx.directives.code import LiteralInclude, CodeBlock
from sphinx.locale import __
from sphinx.ext.doctest import DocTestBuilder
from sphinx.util.docutils import SphinxDirective


@contextlib.contextmanager
def chdir(new_path):
    """
    Context manager to change directroy
    """
    old_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(old_path)


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

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        pass


class CDCommand(ConsoletestCommand):
    def __init__(self, directory: str):
        super().__init__()
        self.directory = directory

    def __eq__(self, other: "CDCommand"):
        return bool(
            hasattr(other, "directory") and self.directory == other.directory
        )

    async def run(self, ctx):
        ctx["cwd"] = os.path.abspath(os.path.join(ctx["cwd"], self.directory))


class ActivateVirtualEnvCommand(ConsoletestCommand):
    def __init__(self, directory: str):
        super().__init__()
        self.directory = directory
        self.old_virtual_env = None
        self.old_path = None
        self.old_sys_path = []

    def __eq__(self, other: "ActivateVirtualEnvCommand"):
        return bool(
            hasattr(other, "directory") and self.directory == other.directory
        )

    async def run(self, ctx):
        self.old_virtual_env = os.environ.get("VIRTUAL_ENV", None)
        self.old_path = os.environ.get("PATH", None)
        env_path = os.path.abspath(os.path.join(ctx["cwd"], self.directory))
        os.environ["PATH"] = ":".join(
            [os.path.join(env_path, "bin")]
            + os.environ.get("PATH", "").split(":")
        )
        # conda
        if "CONDA_PREFIX" in os.environ:
            print("CONDA")
            # Bump all prefixes up
            for key, value in filter(
                lambda i: i[0].startswith("CONDA_PREFIX_"),
                list(os.environ.items()),
            ):
                prefix = int(key[len("CONDA_PREFIX_") :])
                os.environ[f"CONDA_PREFIX_{prefix + 1}"] = value
            # Add new prefix
            old_shlvl = int(os.environ["CONDA_SHLVL"])
            os.environ["CONDA_SHLVL"] = str(old_shlvl + 1)
            os.environ["CONDA_PREFIX_1"] = os.environ["CONDA_PREFIX"]
            os.environ["CONDA_PREFIX"] = env_path
            os.environ["CONDA_DEFAULT_ENV"] = env_path
        else:
            print("VIRTUAL_ENV")
            os.environ["VIRTUAL_ENV"] = env_path

        return

        # TODO Related to the coverage issue
        importlib.invalidate_caches()

        # Remove old site-packages and replace it with the one from the
        # virtual environment
        sys.path[:] = list(
            filter(lambda i: f"lib{os.sep}python" in i, sys.path)
        )
        for i, entry in enumerate(sys.path):
            if entry.endswith("site-packages"):
                sys.path[i] = os.path.abspath(
                    os.path.join(
                        ctx["cwd"],
                        self.directory,
                        "lib",
                        f"python{sys.version_info.major}.{sys.version_info.minor}",
                        "site-packages",
                    )
                )

        pkg_resources = importlib.import_module("pkg_resources")
        importlib.reload(pkg_resources)

        # Replace the working_set so that iter_entry_points will work
        working_set = pkg_resources.WorkingSet([])
        for entry in sys.path:
            if entry not in working_set.entries:
                working_set.add_entry(entry)
        pkg_resources.working_set = working_set

        print(sys.path)

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        if self.old_virtual_env is not None:
            os.environ["VIRTUAL_ENV"] = self.old_virtual_env
        if self.old_path is not None:
            os.environ["PATH"] = self.old_path
        # conda
        if "CONDA_PREFIX" in os.environ:
            # Decrement shell level
            os.environ["CONDA_SHLVL"] = str(int(os.environ["CONDA_SHLVL"]) - 1)
            if int(os.environ["CONDA_SHLVL"]) == 0:
                del os.environ["CONDA_SHLVL"]
            # Bump all prefixes down
            for key, value in filter(
                lambda i: i[0].startswith("CONDA_PREFIX_"),
                list(os.environ.items()),
            ):
                del os.environ[key]
                prefix = int(key[len("CONDA_PREFIX_") :])
                if prefix == 1:
                    lower_key = "CONDA_PREFIX"
                    os.environ["CONDA_PREFIX"] = value
                    os.environ["CONDA_DEFAULT_ENV"] = value
                else:
                    os.environ[f"CONDA_PREFIX_{prefix - 1}"] = value
        return

        # TODO Related to the coverage issue
        if self.old_sys_path:
            sys.path[:] = self.old_sys_path


class HTTPServerCMDDoesNotHavePortFlag(Exception):
    pass


@contextlib.asynccontextmanager
async def start_http_server(cmd):
    # Reload in case we've entered a virtualenv
    http_service_testing = importlib.import_module(
        "dffml_service_http.util.testing"
    )
    importlib.reload(http_service_testing)
    http_service_cli = importlib.import_module("dffml_service_http.cli")
    importlib.reload(http_service_cli)
    async with http_service_testing.ServerRunner.patch(
        http_service_cli.HTTPService.server
    ) as tserver:
        # Start the HTTP server
        cli = await tserver.start(
            http_service_cli.HTTPService.server.cli(*cmd)
        )
        yield cli.port


class DFFMLProcess:
    def __init__(self):
        self.stdout = io.StringIO()
        self.background = None
        self.returncode: int = 0
        return

    async def wait(self):
        return

    async def stop(self):
        if self.background is not None:
            await self.background.__aexit__(None, None, None)


async def run_dffml_command(cmd, ctx, kwargs):
    # Run the DFFML command if its not the http server
    if cmd[:4] != ["dffml", "service", "http", "server"]:
        # Run the command
        proc = subprocess.Popen(
            cmd, start_new_session=True, cwd=ctx["cwd"], **kwargs
        )
        proc.cmd = cmd
    else:
        # Windows won't let two processes open a file at the same time
        with tempfile.TemporaryDirectory() as tempdir:
            # Ensure that the HTTP server is being started with an explicit port
            if "-port" not in cmd:
                raise HTTPServerCMDDoesNotHavePortFlag(cmd)
            # Add logging
            cmd.insert(cmd.index("server") + 1, "debug")
            cmd.insert(cmd.index("server") + 1, "-log")
            # Add the -portfile flag to make the server write out the bound port
            # number
            portfile_path = pathlib.Path(tempdir, "portfile.int").resolve()
            cmd.insert(cmd.index("server") + 1, str(portfile_path))
            cmd.insert(cmd.index("server") + 1, "-portfile")
            # Save the port the command gave
            ctx.setdefault("HTTP_SERVER", {})
            given_port = cmd[cmd.index("-port") + 1]
            ctx["HTTP_SERVER"][given_port] = 0
            # Replace the port that was given with port 0 to bind on any free
            # port
            cmd[cmd.index("-port") + 1] = "0"
            # Run the command
            proc = subprocess.Popen(
                cmd, start_new_session=True, cwd=ctx["cwd"], **kwargs
            )
            proc.cmd = cmd
            # Read the file containing the port number
            while proc.returncode is None:
                if portfile_path.is_file():
                    port = int(portfile_path.read_text())
                    break
                await asyncio.sleep(0.01)
            # Map the port that was given to the port that was used
            ctx["HTTP_SERVER"][given_port] = port
    # Return the newly created process
    return proc

    # TODO the below code is because coverage won't go through subprocess
    # invocations. IT wasn't working though do to issues with importlib causing
    # instances of loaded classes within each module to be different
    # (issubclass(loaded, CMD) in Service of dffml/cli/cli.py.

    # If the command is dffml then import it and run it instead of a
    # subprocess so that we get coverage information
    importlib.invalidate_caches()
    for key, value in sys.modules.items():
        if key.startswith("dffml"):
            importlib.reload(value)
    # If the command is dffml then import it and run it instead of a
    # subprocess so that we get coverage information
    # dffml_util_cli = importlib.import_module("dffml.util.cli.cmd")
    # importlib.reload(dffml_util_cli)
    # dffml_cli = importlib.import_module("dffml.cli.cli")
    # importlib.reload(dffml_cli)
    # Create the process
    proc = DFFMLProcess()
    # Use an ExitStack for standard in, out, and error redirection
    with contextlib.ExitStack() as stack:
        # Change directory to the current working directory
        stack.enter_context(chdir(ctx["cwd"]))
        # Run the DFFML command if its not the http server
        if cmd[:4] != ["dffml", "service", "http", "server"]:
            # Make sure the stdout of this command gets redirected
            stdout = kwargs["stdout"]
            if stdout == subprocess.PIPE:
                stdout = proc.stdout
            with contextlib.redirect_stdout(stdout):
                # Remove leading "dffml" from command
                result = await dffml_cli.CLI._main(*cmd[1:])
                if result == dffml_util_cli.DisplayHelp:
                    raise RuntimeError(f"dffml command failed: {cmd}")
        else:
            # Ensure that the HTTP server is being started with an explit port
            if "-port" not in cmd:
                raise HTTPServerCMDDoesNotHavePortFlag(cmd)
            # Save the port the command gave
            ctx.setdefault("HTTP_SERVER", {})
            given_port = cmd[cmd.index("-port") + 1]
            ctx["HTTP_SERVER"][given_port] = 0
            # Replace the port that was given with port 0 to bind on any free
            # port
            cmd[cmd.index("-port") + 1] = "0"
            # Create a wrapper around the async server starting
            server = start_http_server(cmd)
            # Map the port that was given to the port that was used
            ctx["HTTP_SERVER"][given_port] = await server.__aenter__()
            # The server running in the background is the process
            proc.background = server
    return proc


@contextlib.contextmanager
def tmpenv(cmd: List[str]) -> List[str]:
    """
    Handle temporary environment variables prepended to command
    """
    oldvars = {}
    tmpvars = {}
    for var in cmd:
        if "=" not in var:
            break
        cmd.pop(0)
        key, value = var.split("=", maxsplit=1)
        tmpvars[key] = value
        if key in os.environ:
            oldvars[key] = os.environ[key]
        os.environ[key] = value
    try:
        yield cmd
    finally:
        for key in tmpvars.keys():
            del os.environ[key]
        for key, value in oldvars.items():
            os.environ[key] = value


async def run_commands(
    cmds,
    ctx,
    *,
    stdin: Union[IO] = None,
    stdout: Union[IO] = None,
    ignore_errors: bool = False,
    daemon: bool = False,
    replace: Optional[str] = None,
):
    proc = None
    procs = []
    for i, cmd in enumerate(map(sub_env_vars, cmds)):
        # Run find replace on command if given
        if replace:
            cmd = call_replace(replace, cmd, ctx)
        # Keyword arguments for Popen
        kwargs = {}
        # Set stdout to system stdout so it doesn't go to the pty
        kwargs["stdout"] = stdout if stdout is not None else sys.stdout
        # Check if there is a previous command
        kwargs["stdin"] = stdin if stdin is not None else subprocess.DEVNULL
        if i != 0:
            # XXX asyncio.create_subprocess_exec doesn't work for piping output
            # from one process to the next. It will complain about stdin not
            # having a fileno()
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
        # Handle temporary environment variables prepended to command
        with tmpenv(cmd) as cmd:
            if cmd[0] == "dffml":
                # Run dffml command through Python so that we capture coverage info
                proc = await run_dffml_command(cmd, ctx, kwargs)
            else:
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
    if daemon or (
        isinstance(procs[-1], DFFMLProcess)
        and procs[-1].background is not None
    ):
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
        self.replace = None
        self.stdin = None
        self.stack = contextlib.ExitStack()

    async def run(self, ctx):
        if self.poll_until is None:
            self.daemon_proc = await run_commands(
                pipes(self.cmd),
                ctx,
                stdin=self.stdin,
                ignore_errors=self.ignore_errors,
                daemon=self.daemon,
                replace=self.replace,
            )
        else:
            while True:
                with tempfile.TemporaryFile() as stdout:
                    await run_commands(
                        pipes(self.cmd),
                        ctx,
                        stdin=self.stdin,
                        stdout=stdout,
                        ignore_errors=self.ignore_errors,
                        replace=self.replace,
                    )
                    stdout.seek(0)
                    stdout = stdout.read().decode()
                    if call_poll_until(self.poll_until, stdout):
                        return
                time.sleep(0.1)

    async def __aenter__(self):
        self.stack.__enter__()
        if self.stdin is not None:
            fileobj = self.stack.enter_context(tempfile.TemporaryFile())
            fileobj.write(self.stdin.encode())
            fileobj.seek(0)
            self.stdin = fileobj
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        # Send ctrl-c to daemon if running
        if self.daemon_proc is not None:
            if isinstance(self.daemon_proc, DFFMLProcess):
                await self.daemon_proc.stop()
            else:
                self.daemon_proc.send_signal(signal.SIGINT)
                self.daemon_proc.wait()
        self.stack.__exit__(None, None, None)


class CreateVirtualEnvCommand(ConsoleCommand):
    def __init__(self, directory: str):
        super().__init__([])
        self.directory = directory

    def __eq__(self, other: "CreateVirtualEnvCommand"):
        return bool(
            hasattr(other, "directory") and self.directory == other.directory
        )

    async def run(self, ctx):
        if "CONDA_PREFIX" in os.environ:
            self.cmd = [
                "conda",
                "create",
                f"python={sys.version_info.major}.{sys.version_info.minor}",
                "-y",
                "-p",
                self.directory,
            ]
        else:
            self.cmd = ["python", "-m", "venv", self.directory]
        await super().run(ctx)


class PipInstallCommand(ConsoleCommand):
    def __init__(self, cmd: List[str]):
        super().__init__(cmd)
        self.directories: List[str] = []
        self.fix_dffml_packages()

    def fix_dffml_packages(self):
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
        for i, pkg in enumerate(self.cmd):
            if "[" in pkg and "]" in pkg:
                for package_name in package_names_to_directory.keys():
                    if pkg.startswith(package_name + "["):
                        pkg, extras = pkg.split("[", maxsplit=1)
                        directory = package_names_to_directory[pkg]
                        directory = os.path.join(ROOT_DIR, *directory)
                        directory = os.path.abspath(directory)
                        self.cmd[i] = directory + "[" + extras
                        if self.cmd[i - 1] != "-e":
                            self.cmd.insert(i, "-e")
                        self.directories.append(directory)
            elif pkg in package_names_to_directory:
                directory = package_names_to_directory[pkg]
                directory = os.path.join(ROOT_DIR, *directory)
                directory = os.path.abspath(directory)
                self.cmd[i] = directory
                if self.cmd[i - 1] != "-e":
                    self.cmd.insert(i, "-e")
                self.directories.append(directory)

    async def pip_has_use_feature(self, ctx):
        with tempfile.TemporaryFile() as stdout:
            with contextlib.redirect_stdout(stdout):
                await run_commands([["python", "-m", "pip", "-h"]], ctx)
                stdout.seek(0)
                return "--use-feature" in stdout.read().decode()

    async def run(self, ctx):
        # Add --use-feature=2020-resolver to pip if it has it
        if await self.pip_has_use_feature(ctx):
            self.cmd.insert(
                self.cmd.index("install") + 1, "--use-feature=2020-resolver"
            )

        await super().run(ctx)

        return

        # TODO Related to the coverage issue
        for path in self.directories:
            sys.path.append(path)

        importlib.invalidate_caches()

        pkg_resources = importlib.import_module("pkg_resources")
        importlib.reload(pkg_resources)

        # Replace the working_set so that iter_entry_points will work
        working_set = pkg_resources.WorkingSet([])
        for entry in sys.path:
            if entry not in working_set.entries:
                working_set.add_entry(entry)
        pkg_resources.working_set = working_set

    async def __aexit__(self, _exc_type, _exc_value, traceback):
        return
        # TODO Related to the coverage issue
        for path in self.directories:
            sys.path.remove(path)


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

    async def __aenter__(self):
        atexit.register(self.cleanup)
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
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
    # Handle virtualenv creation
    if (
        "-m" in cmd and "venv" in cmd and cmd[cmd.index("-m") + 1] == "venv"
    ) or (cmd[:2] == ["conda", "create"]):
        return CreateVirtualEnvCommand(cmd[-1])
    # Handle virtualenv activation
    if ".\\.venv\\Scripts\\activate" in cmd or (
        len(cmd) == 2
        and cmd[0] in ("source", ".")
        and ".venv/bin/activate" == cmd[1]
    ):
        return ActivateVirtualEnvCommand(".venv")
    # Handle cd
    if "cd" == cmd[0]:
        return CDCommand(cmd[1])
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


MAKE_REPLACE_UNTIL_TEMPLATE = """
import sys
import json
import pathlib

cmd = json.loads(pathlib.Path(sys.argv[1]).read_text())
ctx = json.loads(pathlib.Path(sys.argv[2]).read_text())

{func}

print(json.dumps(cmd))
"""


def call_replace(func: str, cmd: List[str], ctx: Dict[str, Any]) -> List[str]:
    with contextlib.ExitStack() as stack:
        # Write out Python script
        python_fileobj = stack.enter_context(tempfile.NamedTemporaryFile())
        python_fileobj.write(
            MAKE_REPLACE_UNTIL_TEMPLATE.format(func=func).encode()
        )
        python_fileobj.seek(0)
        # Write out command
        cmd_fileobj = stack.enter_context(tempfile.NamedTemporaryFile())
        cmd_fileobj.write(json.dumps(cmd).encode())
        cmd_fileobj.seek(0)
        # Write out context
        ctx_fileobj = stack.enter_context(tempfile.NamedTemporaryFile())
        ctx_fileobj.write(json.dumps(ctx).encode())
        ctx_fileobj.seek(0)
        # Python file modifies command and json.dumps result to stdout
        return json.loads(
            subprocess.check_output(
                [
                    "python",
                    python_fileobj.name,
                    cmd_fileobj.name,
                    ctx_fileobj.name,
                ],
            )
        )


# Override the literalinclude directive's run method so we can pick up the flags
# we've added
def LiteralInclude_run(func):
    @functools.wraps(func)
    def wrapper(self) -> List[Node]:
        retnodes = func(self)

        if "test" in self.options:
            retnodes[0]["consoletestnodetype"] = "consoletest-literalinclude"
            retnodes[0]["lines"] = self.options.get("lines", None)
            retnodes[0]["filepath"] = self.options.get(
                "filepath", os.path.basename(retnodes[0]["source"])
            ).split("/")

        return retnodes

    return wrapper


LiteralInclude.run = LiteralInclude_run(LiteralInclude.run)


LiteralInclude.option_spec.update(
    {"filepath": directives.unchanged_required, "test": directives.flag}
)


# Override the code-block directive's run method so we can pick up the flags
# we've added
def CodeBlock_run(func):
    @functools.wraps(func)
    def wrapper(self) -> List[Node]:
        retnodes = func(self)

        if "filepath" in self.options:
            node = retnodes[0]
            node["consoletestnodetype"] = "consoletest-file"
            node["content"] = self.content
            node["filepath"] = self.options["filepath"].split("/")
        elif "test" in self.options:
            node = retnodes[0]
            node.setdefault("language", "console")
            node["consoletestnodetype"] = "consoletest"
            node["consoletest_commands"] = list(
                map(build_command, parse_commands(self.content))
            )

            for command in node["consoletest_commands"]:
                command.replace = self.options.get("replace", None)
                command.poll_until = self.options.get("poll-until", None)
                command.ignore_errors = bool("ignore-errors" in self.options)
                command.stdin = self.options.get("stdin", None)

            # Last command to be run is a daemon
            daemon = bool("daemon" in self.options)
            if daemon:
                node["consoletest_commands"][-1].daemon = True

        return retnodes

    return wrapper


CodeBlock.run = CodeBlock_run(CodeBlock.run)

CodeBlock.option_spec.update(
    {
        "filepath": directives.unchanged_required,
        "replace": directives.unchanged_required,
        "poll-until": directives.unchanged_required,
        "ignore-errors": directives.flag,
        "daemon": directives.flag,
        "test": directives.flag,
        "stdin": directives.unchanged_required,
    }
)


def copyfile(
    src: str, dst: str, *, lines: Optional[Union[int, Tuple[int, int]]] = None
) -> None:
    dst_path = pathlib.Path(dst)
    if not dst_path.parent.is_dir():
        dst_path.parent.mkdir(parents=True)

    if not lines:
        shutil.copyfile(src, dst)
        return

    with open(src, "rt") as infile, open(dst, "at") as outfile:
        outfile.seek(0, io.SEEK_END)
        for i, line in enumerate(infile):
            # Line numbers start at 1
            i += 1
            if len(lines) == 1 and i == lines[0]:
                outfile.write(line)
                break
            elif i >= lines[0] and i <= lines[1]:
                outfile.write(line)
            elif i > lines[1]:
                break


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
        return (
            isinstance(node, (nodes.literal_block, nodes.comment))
            and "consoletestnodetype" in node
        )

    async def _test_doc(
        self, docname: str, doc_nodes: List[Node], stack: contextlib.ExitStack,
    ) -> None:
        async with contextlib.AsyncExitStack() as astack:
            tempdir = stack.enter_context(tempfile.TemporaryDirectory())
            venvdir = stack.enter_context(tempfile.TemporaryDirectory())

            ctx = {"cwd": tempdir}
            venvdir = os.path.abspath(venvdir)

            # Create a virtualenv for every document
            for command in [
                CreateVirtualEnvCommand(venvdir),
                ActivateVirtualEnvCommand(venvdir),
                PipInstallCommand(
                    [
                        "python",
                        "-m",
                        "pip",
                        "install",
                        "-U",
                        "pip",
                        "setuptools",
                        "wheel",
                        "dffml",
                    ]
                ),
            ]:
                print()
                print("Running", ctx, command)
                print()
                await astack.enter_async_context(command)
                await command.run(ctx)

            for node in doc_nodes:  # type: Element
                filename = self.get_filename_for_node(node, docname)
                line_number = self.get_line_number(node)

                if node["consoletestnodetype"] == "consoletest-literalinclude":
                    lines = node.get("lines", None)
                    if lines is not None:
                        lines = tuple(map(int, lines.split("-")))

                    src = os.path.join(ROOT_DIR, "docs", node["source"])
                    dst = os.path.join(ctx["cwd"], *node["filepath"])

                    print()
                    print("Copying", ctx, src, dst, lines)

                    copyfile(src, dst, lines=lines)
                    print(pathlib.Path(dst).read_text(), end="")
                    print()
                elif node["consoletestnodetype"] == "consoletest-file":
                    print()
                    filepath = pathlib.Path(ctx["cwd"], *node["filepath"])
                    print("Writing", ctx, filepath)

                    if not filepath.parent.is_dir():
                        filepath.parent.mkdir(parents=True)

                    filepath.write_text("\n".join(node["content"]) + "\n")

                    print(filepath.read_text(), end="")
                    print()
                elif node["consoletestnodetype"] == "consoletest":
                    for command in node["consoletest_commands"]:
                        print()
                        print("Running", ctx, command)
                        print()
                        await astack.enter_async_context(command)
                        await command.run(ctx)

    def test_doc(self, docname: str, doctree: Node) -> None:
        # Get all applicable nodes
        doc_nodes = list(doctree.traverse(self.condition))

        if not doc_nodes:
            return

        print()
        print(f"{self.name} testing: {docname}")
        print()

        self.total_tries += 1

        watcher = asyncio.get_child_watcher()
        loop = asyncio.new_event_loop()
        watcher.attach_loop(loop)

        def cleanup():
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

        # The stack that holds the temporary directories which contain the
        # current working directory must be unwound *after*
        # loop.shutdown_asyncgens() is called. This is to ensure that if any of
        # the generators use those directories, they still have access to them
        # (pdxjohnny) I'm not entirely sure if the above statement is true. I
        # was testing the shutdown of the HTTP server interacting with the model
        # directory and it didn't seem to work if I remember correctly.
        with contextlib.ExitStack() as stack:
            try:
                loop.run_until_complete(
                    self._test_doc(docname, doc_nodes, stack)
                )
                cleanup()
            except:
                cleanup()
                self.total_failures += 1
                traceback.print_exc(file=sys.stderr)

        print()
        print("No more tempdir")
        print()


def setup(app: "Sphinx") -> Dict[str, Any]:
    app.add_builder(ConsoleTestBuilder)
    return {"version": "0.0.1", "parallel_read_safe": True}
