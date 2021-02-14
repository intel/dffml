"""
Running of shell commands
"""
import os
import abc
import sys
import json
import time
import copy
import shlex
import signal
import atexit
import asyncio
import pathlib
import inspect
import tempfile
import contextlib
import subprocess
from typing import IO, Any, Dict, List, Union, Optional

from .... import plugins


DFFML_ROOT = pathlib.Path(__file__).parents[4]


class ConsoletestCommand(abc.ABC):
    def __init__(self):
        self.poll_until = False
        self.compare_output = None
        self.compare_output_imports = None
        self.ignore_errors = False
        self.daemon = None

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
        self.old_virtual_env_dir = None
        self.old_path = None
        self.old_pythonpath = None
        self.old_sys_path = []

    def __eq__(self, other: "ActivateVirtualEnvCommand"):
        return bool(
            hasattr(other, "directory") and self.directory == other.directory
        )

    async def run(self, ctx):
        tempdir = ctx["stack"].enter_context(tempfile.TemporaryDirectory())
        self.old_virtual_env = os.environ.get("VIRTUAL_ENV", None)
        self.old_virtual_env_dir = os.environ.get("VIRTUAL_ENV_DIR", None)
        self.old_path = os.environ.get("PATH", None)
        self.old_pythonpath = os.environ.get("PYTHONPATH", None)
        env_path = os.path.abspath(os.path.join(ctx["cwd"], self.directory))
        os.environ["PATH"] = ":".join(
            [os.path.abspath(tempdir), os.path.join(env_path, "bin")]
            + os.environ.get("PATH", "").split(":")
        )
        os.environ["PYTHONPATH"] = ":".join(
            os.environ.get("PYTHONPATH", "").split(":")
            + [
                os.path.join(
                    env_path,
                    "lib",
                    f"python{sys.version_info.major}.{sys.version_info.minor}",
                    "site-packages",
                )
            ],
        )
        # conda
        if "CONDA_PREFIX" in os.environ:
            print("CONDA", env_path)
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
            print("VIRTUAL_ENV", env_path)
            os.environ["VIRTUAL_ENV"] = env_path
            os.environ["VIRTUAL_ENV_DIR"] = env_path

        for env_var in ["VIRTUAL_ENV", "CONDA_PREFIX"]:
            if env_var in os.environ:
                python_path = os.path.abspath(
                    os.path.join(os.environ[env_var], "bin", "python")
                )
        # Prepend a dffml command to the path to ensure the correct
        # version of dffml always runs
        # Write out the file
        dffml_path = pathlib.Path(os.path.abspath(tempdir), "dffml")
        dffml_path.write_text(
            inspect.cleandoc(
                f"""
            #!{python_path}
            import os
            import sys

            os.execv("{python_path}", ["{python_path}", "-m", "dffml", *sys.argv[1:]])
            """
            )
        )
        dffml_path.chmod(0o755)

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        if self.old_virtual_env is not None:
            os.environ["VIRTUAL_ENV"] = self.old_virtual_env
        if self.old_virtual_env_dir is not None:
            os.environ["VIRTUAL_ENV_DIR"] = self.old_virtual_env_dir
        if self.old_path is not None:
            os.environ["PATH"] = self.old_path
        if self.old_pythonpath is not None:
            os.environ["PYTHONPATH"] = self.old_pythonpath
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


class HTTPServerCMDDoesNotHavePortFlag(Exception):
    pass


async def run_dffml_command(cmd, ctx, kwargs):
    # Run the DFFML command if its not the http server
    if cmd[:4] != ["dffml", "service", "http", "server"]:
        # Run the command
        print()
        print("Running", cmd)
        print()
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
            print()
            print("Running", cmd)
            print()
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
):
    proc = None
    procs = []
    cmds = list(map(sub_env_vars, cmds))
    for i, cmd in enumerate(cmds):
        # Keyword arguments for Popen
        kwargs = {}
        # Set stdout to system stdout so it doesn't go to the pty
        kwargs["stdout"] = stdout if stdout is not None else sys.stdout
        # Check if there is a previous command
        kwargs["stdin"] = stdin if stdin is not None else subprocess.DEVNULL
        if i != 0:
            # NOTE asyncio.create_subprocess_exec doesn't work for piping output
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
        if (
            "VIRTUAL_ENV" not in os.environ
            and "CONDA_PREFIX" not in os.environ
            and cmd[0].startswith("python")
        ):
            cmd[0] = sys.executable
        # Handle temporary environment variables prepended to command
        with tmpenv(cmd) as cmd:
            # Run the command
            if cmd[0] == "dffml":
                # Run dffml command through Python so that we capture coverage info
                proc = await run_dffml_command(cmd, ctx, kwargs)
            else:
                # Run the command
                print()
                print("Running", cmd)
                print()
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


async def stop_daemon(proc):
    # Send ctrl-c to daemon if running
    proc.send_signal(signal.SIGINT)
    proc.wait()


class OutputComparisionError(Exception):
    """
    Raised when the output of a command was incorrect
    """


@contextlib.contextmanager
def buf_to_fileobj(buf: Union[str, bytes]):
    """
    Given a buffer, create a temporary file and write the contents of the string
    of bytes buffer to the file. Seek to the beginning of the file. Yield the
    file object.
    """
    if isinstance(buf, str):
        buf = buf.encode()
    with tempfile.TemporaryFile() as fileobj:
        fileobj.write(buf)
        fileobj.seek(0)
        yield fileobj


class ConsoleCommand(ConsoletestCommand):
    def __init__(self, cmd: List[str]):
        super().__init__()
        self.cmd = cmd
        self.daemon_proc = None
        self.replace = None
        self.stdin = None
        self.stdin_fileobj = None
        self.stack = contextlib.ExitStack()

    async def run(self, ctx):
        if self.daemon is not None and self.daemon in ctx["daemons"]:
            await stop_daemon(ctx["daemons"][self.daemon].daemon_proc)
        if self.compare_output is None:
            with contextlib.ExitStack() as stack:
                self.daemon_proc = await run_commands(
                    pipes(self.cmd),
                    ctx,
                    stdin=None
                    if self.stdin is None
                    else stack.enter_context(buf_to_fileobj(self.stdin)),
                    ignore_errors=self.ignore_errors,
                    daemon=bool(self.daemon),
                )
                if self.daemon is not None:
                    ctx["daemons"][self.daemon] = self
        else:
            while True:
                with contextlib.ExitStack() as stack:
                    stdout = stack.enter_context(tempfile.TemporaryFile())
                    await run_commands(
                        pipes(self.cmd),
                        ctx,
                        stdin=None
                        if self.stdin is None
                        else stack.enter_context(buf_to_fileobj(self.stdin)),
                        stdout=stdout,
                        ignore_errors=self.ignore_errors,
                    )
                    stdout.seek(0)
                    stdout = stdout.read()
                    if call_compare_output(
                        self.compare_output,
                        stdout,
                        imports=self.compare_output_imports,
                    ):
                        return
                if not self.poll_until:
                    raise OutputComparisionError(
                        f"{self.cmd}: {self.compare_output}: {stdout.decode()}"
                    )
                time.sleep(0.1)

    async def __aenter__(self):
        self.stack.__enter__()
        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        if self.daemon_proc is not None:
            await stop_daemon(self.daemon_proc)
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


class PipNotRunAsModule(Exception):
    """
    Raised when a pip install command was not prefixed with python -m to run pip
    as a module. Pip sometimes complains when this is not done.
    """


class PipInstallCommand(ConsoleCommand):
    def __init__(self, cmd: List[str]):
        super().__init__(cmd)
        self.directories: List[str] = []
        # Ensure that we are running pip using it's module invocation
        if self.cmd[:2] != ["python", "-m"]:
            raise PipNotRunAsModule(cmd)

    def fix_dffml_packages(self, ctx):
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
                        directory = os.path.join(DFFML_ROOT, *directory)
                        directory = os.path.abspath(directory)
                        self.cmd[i] = directory + "[" + extras
                        if self.cmd[i - 1] != "-e":
                            self.cmd.insert(i, "-e")
                        self.directories.append(directory)
            elif pkg in package_names_to_directory:
                directory = package_names_to_directory[pkg]
                directory = os.path.join(DFFML_ROOT, *directory)
                directory = os.path.abspath(directory)
                self.cmd[i] = directory
                if self.cmd[i - 1] != "-e":
                    self.cmd.insert(i, "-e")
                self.directories.append(directory)

    async def run(self, ctx):
        # In case a replace command changed something
        self.fix_dffml_packages(ctx)

        await super().run(ctx)

        # Remove dataclasses. See https://github.com/intel/dffml/issues/882
        # TODO(p0,security) Audit this
        remove_dataclasses_path = (
            DFFML_ROOT
            / "scripts"
            / "tempfix"
            / "pytorch"
            / "pytorch"
            / "46930.py"
        )
        if not remove_dataclasses_path.is_file():
            return

        cmd = ["python", str(remove_dataclasses_path)]
        if "CONDA_PREFIX" in os.environ:
            cmd.append(os.environ["CONDA_PREFIX"])
        elif "VIRTUAL_ENV" in os.environ:
            cmd.append(os.environ["VIRTUAL_ENV"])
        await run_commands([cmd], ctx)

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        return


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
{imports}

func = lambda stdout: {func}

sys.exit(int(not func(sys.stdin.buffer.read())))
"""


def call_compare_output(func, stdout, *, imports: Optional[str] = None):
    with tempfile.NamedTemporaryFile() as fileobj, tempfile.NamedTemporaryFile() as stdin:
        fileobj.write(
            MAKE_POLL_UNTIL_TEMPLATE.format(
                func=func,
                imports="" if imports is None else "import " + imports,
            ).encode()
        )
        fileobj.seek(0)
        stdin.write(stdout.encode() if isinstance(stdout, str) else stdout)
        stdin.seek(0)
        return_code = subprocess.call(["python", fileobj.name], stdin=stdin)
        return bool(return_code == 0)


MAKE_REPLACE_UNTIL_TEMPLATE = """
import sys
import json
import pathlib

cmds = json.loads(pathlib.Path(sys.argv[1]).read_text())
ctx = json.loads(pathlib.Path(sys.argv[2]).read_text())

{func}

print(json.dumps(cmds))
"""


def call_replace(
    func: str, cmds: List[List[str]], ctx: Dict[str, Any]
) -> List[List[str]]:
    with contextlib.ExitStack() as stack:
        # Write out Python script
        python_fileobj = stack.enter_context(tempfile.NamedTemporaryFile())
        python_fileobj.write(
            MAKE_REPLACE_UNTIL_TEMPLATE.format(func=func).encode()
        )
        python_fileobj.seek(0)
        # Write out command
        cmd_fileobj = stack.enter_context(tempfile.NamedTemporaryFile())
        cmd_fileobj.write(json.dumps(cmds).encode())
        cmd_fileobj.seek(0)
        # Write out context
        ctx_fileobj = stack.enter_context(tempfile.NamedTemporaryFile())
        ctx_serializable = ctx.copy()
        for remove in list(ctx["no_serialize"]) + ["no_serialize"]:
            if remove in ctx_serializable:
                del ctx_serializable[remove]
        ctx_fileobj.write(json.dumps(ctx_serializable).encode())
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
