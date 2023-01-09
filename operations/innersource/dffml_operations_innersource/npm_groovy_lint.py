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
)


NPMGroovyLintCMD = NewType("NPMGroovyLintCMD", str)
NPMGroovyLintResult = NewType("NPMGroovyLintResult", str)
JavaBinary = NewType("JavaBinary", str)
CodeNarcServerProc = NewType("CodeNarcServerProc", object)
CodeNarcServerReturnCode = NewType("CodeNarcServerReturnCode", int)


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
    java_lib_path = npm_groovy_lint_cmd[1].resolve().parents[1].joinpath(
        "lib", "java",
    )
    # Run the server
    proc = None
    # TODO Port is currently hardcoded, recompile? src/ files in npm-groovy-lint
    async for event, result in dffml.run_command_events(
        [

            java_binary,
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
            if result != 130:
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
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> NPMGroovyLintResult:
    proc = await asyncio.create_subprocess_exec(
        *npm_groovy_lint_cmd,
        "--noserver",
        # It will try to install java unless we give it one
        "--javaexecutable",
        java_binary,
        "--output",
        "json",
        ".",
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
