import json
import signal
import asyncio
import pathlib
import logging
import contextlib
from typing import NewType

import dffml

# from .operations import (
from dffml_operations_innersource.operations import (
    RepoDirectory,
    GroovyFileWorkflowUnixStylePaths,
)


NPMGroovyLintCMD = NewType("NPMGroovyLintCMD", list[str])
NPMGroovyLintResult = NewType("NPMGroovyLintResult", str)
JavaBinary = NewType("JavaBinary", str)
CodeNarcServerProc = NewType("CodeNarcServerProc", object)
CodeNarcServerReturnCode = NewType("CodeNarcServerReturnCode", int)


class CouldNotResolvePathToNPMGroovyLintInstallError(Exception):
    pass


class CodeNarcServerUnknownFailure(Exception):
    pass


@contextlib.asynccontextmanager
async def code_narc_server(
    java_binary: JavaBinary,
    npm_groovy_lint_cmd: NPMGroovyLintCMD,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> CodeNarcServerProc:
    # Path to compiled CodeNarcServer within released package
    npm_groovy_lint_path = npm_groovy_lint_cmd[-1]
    if isinstance(npm_groovy_lint_path, str):
        npm_groovy_lint_path = pathlib.Path(npm_groovy_lint_path)
        if not npm_groovy_lint_path.exists():
            npm_groovy_lint_path = dffml.which(npm_groovy_lint_path.name)
    if not isinstance(npm_groovy_lint_path, pathlib.Path):
        raise CouldNotResolvePathToNPMGroovyLintInstallError(npm_groovy_lint_cmd)
    java_lib_path = npm_groovy_lint_path.resolve().parents[1].joinpath(
        "lib", "java",
    )
    # Run the server
    proc = None
    # TODO Port is currently hardcoded, recompile? src/ files in npm-groovy-lint
    async for event, result in dffml.run_command_events(
        [

            java_binary,
            "-Djava.net.useSystemProxies=true",
            "-Xms256m",
            "-Xmx2048m",
            "-cp",
            (
                str(java_lib_path.joinpath("CodeNarcServer.jar").resolve())
                + ":"
                + str(java_lib_path.joinpath("*").resolve())
            ),
            "com.nvuillam.CodeNarcServer",
            "--server",
            r"includes='{}/.groovy'",
        ],
        env=env,
        logger=logger,
        events=[
            dffml.Subprocess.CREATED,
            dffml.Subprocess.COMPLETED,
        ],
        raise_on_failure=False,
    ):
        if event is dffml.Subprocess.CREATED:
            proc = result
            # TODO Ask for STDOUT_READLINE and wait to yield until we know we
            # can hit the HTTP server?
            try:
                yield proc
            finally:
                # Send Ctrl-C to exit cleanly
                with contextlib.suppress(ProcessLookupError):
                    proc.send_signal(signal.SIGINT)
        elif event is dffml.Subprocess.COMPLETED:
            # Clean exit triggered by Ctrl-C will have a return code as follows
            if result not in (130, -2):
                raise CodeNarcServerUnknownFailure(f"Exit code: {result}")


@dffml.op
async def start_code_narc_server(
    java_binary: JavaBinary,
    npm_groovy_lint_cmd: NPMGroovyLintCMD,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> CodeNarcServerProc:
    proc_context_manager = code_narc_server(
        java_binary,
        npm_groovy_lint_cmd,
        env=env,
        logger=logger,
    )
    proc_context_manager.proc = await proc_context_manager.__aenter__()
    return proc_context_manager


@dffml.op(
    stage=dffml.Stage.CLEANUP,
)
async def stop_code_narc_server(
    proc: CodeNarcServerProc,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> CodeNarcServerReturnCode:
    await proc.__aexit__(None, None, None)
    return proc.proc.returncode


@dffml.op
async def npm_groovy_lint(
    repo_directory: RepoDirectory,
    java_binary: JavaBinary,
    # TODO Port for code narc is currently hardcoded, upstream fix and use here.
    _code_narc_proc: CodeNarcServerProc,
    npm_groovy_lint_cmd: NPMGroovyLintCMD,
    groovy_paths: GroovyFileWorkflowUnixStylePaths,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> NPMGroovyLintResult:
    if not groovy_paths:
        return
    # Check for config file
    config_args = []
    npmgroovylintrc_paths = list(pathlib.Path(repo_directory).rglob(".groovylintrc.json"))
    if npmgroovylintrc_paths:
        if logger and len(npmgroovylintrc_paths) > 1:
            logger.warning("Choosing first config file of multiple found: %r", npmgroovylintrc_paths)
        config_args = ["--config", npmgroovylintrc_paths[0]]
    cmd = [
        *npm_groovy_lint_cmd,
        *config_args,
        "--noserver",
        # It will try to install java unless we give it one
        "--javaexecutable",
        java_binary,
        "--output",
        "json",
        "--",
        *groovy_paths,
    ]
    if logger:
        logger.debug("cmd: %r", cmd)
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=repo_directory,
        env=env,
        stdout=asyncio.subprocess.PIPE,
    )
    work = {
        asyncio.create_task(proc.wait()): "wait",
        asyncio.create_task(proc.communicate()): "communicate",
    }
    async for event, result in dffml.concurrently(work):
        if event == "communicate":
            parsed_result = json.loads(result[0])
            return {
                **parsed_result,
                **{
                    "files": {
                        str(pathlib.Path(path).relative_to(repo_directory)): value
                        for path, value in parsed_result.get("files", {}).items()
                    }
                }
            }
