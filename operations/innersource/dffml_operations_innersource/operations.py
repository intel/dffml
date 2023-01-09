import json
import signal
import pathlib
import logging
import datetime
import platform
import contextlib
from typing import List, NewType

import yaml

import dffml
from dffml_feature_git.feature.definitions import (
    git_repository_checked_out,
    quarter_start_date,
)


GitHubActionsWorkflowUnixStylePath = NewType("GitHubActionsWorkflowUnixStylePath", str)
JenkinsfileWorkflowUnixStylePath = NewType("JenkinsfileWorkflowUnixStylePath", str)
GroovyFileWorkflowUnixStylePath = NewType("GroovyFileWorkflowUnixStylePath", str)
ActionYAMLFileWorkflowUnixStylePath = NewType("ActionYAMLFileWorkflowUnixStylePath", str)

# Check for
#   "usage", "example(s)", "Known issues" (text or link to issue tracker) in docs
#   Support / contact information in docs (issue tracker link)
#   Linting (goovy linter, YAML linting), score it needs to meet
#   CI/CD on library itself (Actions workflows or webhooks configured)
#   We want to check for branch protection
#   We want to make sure that the issues are being addressed (hyptothetical SLA estimates)
#   Libraries should not have any hardcoded settings
#   Credentials must be managed securly and with minimal scope needed
#   Dependencies
#   - Must be explictly documented somewhere (SBOM okay)
#   - All dependnecies should be created by github or github verified createors or within dffml org
#   We should seperate seperate functionality into seperate libraries
#   We should be using symver


def relative_paths(
    directory: str,
    paths: List[str],
):
    return [
        path.relative_to(directory)
        for path in paths
    ]


@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": GitHubActionsWorkflowUnixStylePath},
    expand=["result"],
)
def github_workflows(self, repo: git_repository_checked_out.spec) -> dict:
    return {
        "result": map(
            str,
            relative_paths(
                repo.directory,
                pathlib.Path(repo.directory, ".github", "workflows").glob("*.yml"),
            ),
        ),
    }


@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": JenkinsfileWorkflowUnixStylePath},
    expand=["result"],
)
def jenkinsfiles(self, repo: git_repository_checked_out.spec) -> dict:
    return {
        "result": map(
            str,
            relative_paths(
                repo.directory,
                pathlib.Path(repo.directory).rglob("**/*Jenkinsfile")
            ),
        ),
    }


@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": GroovyFileWorkflowUnixStylePath},
    expand=["result"],
)
def groovy_files(self, repo: git_repository_checked_out.spec) -> dict:
    return {
        "result": map(
            str,
            relative_paths(
                repo.directory,
                [
                    *pathlib.Path(repo.directory).rglob("*.groovy"),
                ],
            ),
        ),
    }

@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": ActionYAMLFileWorkflowUnixStylePath},
    expand=["result"],
)
def action_yml_files(self, repo: git_repository_checked_out.spec) -> dict:
    return {
        "result": map(
            str,
            relative_paths(
                repo.directory,
                pathlib.Path(repo.directory).rglob("**/action.yml")
            ),
        ),
    }


FileReadmePresent = NewType("FileReadmePresent", bool)
FileContributingPresent = NewType("FileContributingPresent", bool)
FileCodeOfConductPresent = NewType("FileCodeOfConductPresent", bool)
FileSecurityPresent = NewType("FileSecurityPresent", bool)
FileSupportPresent = NewType("FileSupportPresent", bool)


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def readme_present(self, repo: git_repository_checked_out.spec) -> FileReadmePresent:
    return any(
        [
            path
            for path in pathlib.Path(repo.directory).iterdir()
            if "readme" == path.stem.lower()
        ]
    )


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def contributing_present(self, repo: git_repository_checked_out.spec) -> FileContributingPresent:
    return any(
        [
            pathlib.Path(repo.directory, "CONTRIBUTING.md").is_file(),
            pathlib.Path(repo.directory, "CONTRIBUTING.rst").is_file()
        ]
    )


# TODO Check compliance with RFC 9116
@dffml.op(inputs={"repo": git_repository_checked_out,},)
def security_present(self, repo: git_repository_checked_out.spec) -> FileSecurityPresent:
    return any(
        [
            pathlib.Path(repo.directory, "SECURITY.md").is_file(),
            pathlib.Path(repo.directory, "SECURITY.rst").is_file(),
            pathlib.Path(repo.directory, "SECURITY.txt").is_file(),
            pathlib.Path(repo.directory, "security.txt").is_file(),
        ]
    )


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def support_present(self, repo: git_repository_checked_out.spec) -> FileSupportPresent:
    return any(
        [
            pathlib.Path(repo.directory, "SUPPORT.md").is_file(),
            pathlib.Path(repo.directory, "SUPPORT.rst").is_file(),
        ]
    )


@dffml.op(inputs={"repo": git_repository_checked_out,},)
def code_of_conduct_present(self, repo: git_repository_checked_out.spec) -> FileCodeOfConductPresent:
    return any(
        [
            pathlib.Path(repo.directory, "CODE_OF_CONDUCT.md").is_file(),
            pathlib.Path(repo.directory, "CODE_OF_CONDUCT.rst").is_file(),
        ]
    )


# TODO Auto definition code which is about to undergo refactor will fix up this
# oddness with typing and half abilty to have auto inputs with types.
@dffml.op(inputs={}, outputs={"result": quarter_start_date})
def get_current_datetime_as_git_date():
    return {
        "result": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


@dffml.op(
    inputs={
        "results": dffml.GroupBy.op.outputs["output"],
    },
    stage=dffml.Stage.OUTPUT,
)
def maintained(results: dict) -> bool:
    return True


@dffml.config
class UnmaintainedConfig:
    commits: int = dffml.field(
        "Any less than this number of commits in the last quarter results in a return value of True",
        default=1,
    )


@dffml.op(
    inputs={
        "results": dffml.GroupBy.op.outputs["output"],
    },
    stage=dffml.Stage.OUTPUT,
    config_cls=UnmaintainedConfig,
)
def unmaintained(self, results: dict) -> bool:
    # As an example, if there are no commits in the last quarter, return
    # unmaintained (True for the unmaintained opreation for this input data).
    if results["commits"][-1] < self.config_cls.commits:
        return True


# TODO We may not need stage anymore, need to see if we should depricate
@dffml.op(
    stage=dffml.Stage.OUTPUT, conditions=[maintained.op.outputs["result"]],
)
def badge_maintained() -> str:
    return "https://img.shields.io/badge/Maintainance-Active-green"


@dffml.op(
    stage=dffml.Stage.OUTPUT, conditions=[unmaintained.op.outputs["result"]],
)
def badge_unmaintained() -> str:
    return "https://img.shields.io/badge/Maintainance-Inactive-red"


RepoDirectory = NewType("RepoDirectory", str)


@dffml.op(
    inputs={"repo": git_repository_checked_out,},
    outputs={"result": RepoDirectory},
)
def repo_directory(self, repo: git_repository_checked_out.spec) -> RepoDirectory:
    # How did this not exist? I think it does somwhere else, another branch
    return {"result": repo.directory}


ActionsValidatorBinary = NewType("ActionsValidatorBinary", str)
ActionsValidatorResult = NewType("ActionsValidatorResult", str)


@dffml.op
async def actions_validator(
    repo_directory: RepoDirectory,
    yaml_file_path: ActionYAMLFileWorkflowUnixStylePath,
    actions_validator_binary: ActionsValidatorBinary,
    *,
    logger: logging.Logger = None,
) -> ActionsValidatorResult:
    """
    >>> import asyncio
    >>> import tempfile
    >>>
    >>> import dffml
    >>> from dffml_operations_innersource.operations import (
    ...     ensure_actions_validator,
    ...     actions_validator,
    ... )
    >>>
    >>> async def main():
    ...     with tempfile.TemporaryDirectory() as tempdir:
    ...         yaml_file_path = pathlib.Path(tempdir).joinpath("action.yml")
    ...         await dffml.cached_download(
    ...             "https://raw.githubusercontent.com/mpalmer/action-validator/dd49fc0db4fc423b32704cc70ad80564d285ded7/test/002_basic_action/action.yml",
    ...             yaml_file_path,
    ...             "fddbaceb0c2d1779438f149db76896764c45a1adea3221b92e481c7a6a72c5ece33ccbb4ef42afc8d03d23b83d02ada9",
    ...         )
    ...         actions_validator_binary = await ensure_actions_validator()
    ...         return await actions_validator(
    ...             tempdir,
    ...             yaml_file_path,
    ...             actions_validator_binary,
    ...         )
    >>>
    >>> print(asyncio.run(main()))
    True
    """
    async for event, result in dffml.run_command_events(
        [
            str(actions_validator_binary),
            str(yaml_file_path),
        ],
        cwd=repo_directory,
        logger=logger,
        events=[
            dffml.Subprocess.STDOUT,
            dffml.Subprocess.STDERR,
            dffml.Subprocess.COMPLETED,
        ],
        raise_on_failure=False,
    ):
        if event is dffml.Subprocess.STDOUT and logger:
            logger.debug("Passed validation: %s", result.decode())
        elif event is dffml.Subprocess.STDERR and logger:
            logger.debug("Failed validation: %s", result.decode())
        elif event is dffml.Subprocess.COMPLETED:
            # TODO Multi output return of stdout / stderr
            return bool(result == 0)


NPMGroovyLintBinary = NewType("NPMGroovyLintBinary", str)
NPMGroovyLintResult = NewType("NPMGroovyLintResult", str)
JavaBinary = NewType("JavaBinary", str)
CodeNarcServerProc = NewType("CodeNarcServerProc", object)
CodeNarcServerReturnCode = NewType("CodeNarcServerReturnCode", int)


class CodeNarcServerUnknownFailure(Exception):
    pass


@contextlib.asynccontextmanager
async def code_narc_server(
    java_binary: JavaBinary,
    npm_groovy_lint_binary: NPMGroovyLintBinary,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> CodeNarcServerProc:
    # Path to compiled CodeNarcServer within released package
    java_lib_path = npm_groovy_lint_binary.resolve().parents[1].joinpath(
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
    npm_groovy_lint_binary: NPMGroovyLintBinary,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> CodeNarcServerProc:
    proc_context_manager = code_narc_server(
        java_binary,
        npm_groovy_lint_binary,
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
async def groovy_lint(
    repo_directory: RepoDirectory,
    # TODO Port for code narc is currently hardcoded, upstream fix and use here.
    _code_narc_proc: CodeNarcServerProc,
    npm_groovy_lint_binary: NPMGroovyLintBinary,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> NPMGroovyLintResult:
    async for event, result in dffml.run_command_events(
        [
            npm_groovy_lint_binary,
            "--noserver",
            "--output",
            "json",
            ".",
        ],
        cwd=repo_directory,
        env=env,
        logger=logger,
        events=[
            dffml.Subprocess.STDOUT,
        ],
        raise_on_failure=False,
    ):
        parsed_result = json.loads(result)
        return {
            **parsed_result,
            **{
                "files": {
                    str(pathlib.Path(path).relative_to(repo_directory)): value
                    for path, value in parsed_result.get("files", {}).items()
                }
            }
        }
