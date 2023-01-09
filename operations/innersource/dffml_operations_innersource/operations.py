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


class _ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS:
    pass


class _ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR:
    pass


ActionsValidatorBinary = NewType("ActionsValidatorBinary", str)
ActionsValidatorCacheDir = NewType("ActionsValidatorCacheDir", str)
ActionsValidatorPlatformURLs = NewType("ActionsValidatorPlatformURLs", str)
ActionsValidatorResult = NewType("ActionsValidatorResult", str)

ACTIONS_VALIDATOR_DEFAULT_BINARY = "actions-validator"
ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR = _ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR()
ACTIONS_VALIDATOR_DEFAULT_CACHE_DIR_PARTS = (
    ".tools", "open-architecture", "innersource", ".cache", "actions-validator",
)
ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS = _ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS()
ACTIONS_VALIDATOR_DEFAULT_PLATFORM_URLS = {
    "Linux": {
        "url": "https://github.com/mpalmer/action-validator/releases/download/v0.2.1/action-validator_linux_amd64",
        "expected_hash": "17d21449f31090efa13fc009be3181121f7c2c4fbe4618b84f4ac66d6bd9ffce21f76193879ddac0f3eec90fe5841280",
    },
}


async def ensure_actions_validator(
    cache_dir: ActionsValidatorCacheDir = ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR,
    platform_urls: ActionsValidatorPlatformURLs = ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS,
) -> ActionsValidatorBinary:
    """

    - References

        - Original sketch of system context with inputs as allow list

            - https://youtu.be/m0TO9IOqRfQ?t=2373&list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK
    - TODOs

        - This operation should be added to the flow during dynamic overlay
          application. Once we have the system context allow list working which
          will tell us which inputs are allowed from which origins (seed,
          client, etc. (see references above for system context sketch).
          At that point, within dynamic overlay application we will inspect the
          system context allow list while we are in the data flow as class
          method construction or whole context call construction to determine if
          the binary is allowed to be passed from caller to callee flow. If it
          does not appear in the allow list, then we will overlay this
          operation. This is a variation on our static overlay, where we apply
          no matter what. In this case, this operation is it's own overlay which
          is applied only if the input is not in the allow list.
    """
    actions_validator_binary_path = pathlib.Path(ACTIONS_VALIDATOR_DEFAULT_BINARY)
    # Ensure we have a copy of the binary
    if (
        not actions_validator_binary_path.exists()
        or not dffml.inpath(actions_validator_binary_path)
    ):
        # Download via given platform to download mapping or use default
        if platform_urls is ACTIONS_VALIDATOR_USE_DEFAULT_PLATFORM_URLS:
            platform_urls = ACTIONS_VALIDATOR_DEFAULT_PLATFORM_URLS
        # Store in given cache directory or create default relative to cwd
        if cache_dir is ACTIONS_VALIDATOR_USE_DEFAULT_CACHE_DIR:
            cache_dir = pathlib.Path(*ACTIONS_VALIDATOR_DEFAULT_CACHE_DIR_PARTS)
        # We don't have a copy of the binary in the path, download it to cache
        actions_validator_binary_path = await dffml.cached_download(
            **{
                "target_path": cache_dir.joinpath("actions-validator"),
                "chmod": 0o755,
                # Use whatever values are appropriate for the system we are on
                **platform_urls[platform.system()],
            }
        )
    return actions_validator_binary_path.resolve()


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


class _NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS:
    pass


class _NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR:
    pass


NPMGroovyLintBinary = NewType("NPMGroovyLintBinary", str)
NPMGroovyLintCacheDir = NewType("NPMGroovyLintCacheDir", str)
NPMGroovyLintPlatformURLs = NewType("NPMGroovyLintPlatformURLs", str)
NPMGroovyLintResult = NewType("NPMGroovyLintResult", str)


NPM_GROOVY_LINT_DEFAULT_BINARY = "npm-groovy-lint"
NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR = _NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR()
NPM_GROOVY_LINT_DEFAULT_CACHE_DIR_PARTS = (
    ".tools", "open-architecture", "innersource", ".cache", "npm-groovy-lint",
)
NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS = _NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS()
# TODO Load all these from a json file using importlib.resources within test bom
NPM_GROOVY_LINT_DEFAULT_PLATFORM_URLS = {
    "Linux": {
        "url": "https://nodejs.org/dist/v14.2.0/node-v14.2.0-linux-x64.tar.xz",
        "expected_hash": "fa2a9dfa4d0f99a0cc3ee6691518c026887677a0d565b12ebdcf9d78341db2066427c9970c41cbf72776a370bbb42729",
    },
}


async def ensure_npm_groovy_lint(
    cache_dir: NPMGroovyLintCacheDir = NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR,
    platform_urls: NPMGroovyLintPlatformURLs = NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> NPMGroovyLintBinary:
    # TODO Take node as arg from ensure_node
    # The location we'll assume the binary is at, its basename, resolved on exec
    # to determine correct path.
    npm_groovy_lint_binary_path = pathlib.Path(NPM_GROOVY_LINT_DEFAULT_BINARY)
    # Bail out if we already have a copy of the binary available in the path,
    # aka that subprocess -> fork + exec will succeed.
    if (
        npm_groovy_lint_binary_path.exists()
        or dffml.inpath(npm_groovy_lint_binary_path)
    ):
        return npm_groovy_lint_binary_path
    # Download via given platform to download mapping or use default
    if platform_urls is NPM_GROOVY_LINT_USE_DEFAULT_PLATFORM_URLS:
        platform_urls = NPM_GROOVY_LINT_DEFAULT_PLATFORM_URLS
    # Store in given cache directory or create default relative to cwd
    if cache_dir is NPM_GROOVY_LINT_USE_DEFAULT_CACHE_DIR:
        cache_dir = pathlib.Path(*NPM_GROOVY_LINT_DEFAULT_CACHE_DIR_PARTS)
    # Download node
    node_install_path = await dffml.cached_download_unpack_archive(
        **{
            "file_path": cache_dir.joinpath("node.tar.gz"),
            "directory_path": cache_dir.joinpath("node-download"),
            # Use whatever values are appropriate for the system we are on
            **platform_urls[platform.system()],
        }
    )
    # Find the binary for nodejs
    node_bin_path = [
        path.parent
        for path in node_install_path.rglob("node")
        if path.parent.name == "bin"
    ][0]
    with dffml.prepend_to_path(*node_bin_path.resolve().parts, env):
        # Run npm to install the package with the binary we are wrapping.
        # Install to the cache dir.
        # In this case npm-groovy-lint
        async for event, result in dffml.run_command_events(
            [
                "npm",
                "i",
                "npm-groovy-lint",
            ],
            cwd=cache_dir,
            env=env,
            logger=logger,
        ):
            pass
        # Create the path to the binary we installed
        node_modules_bin_path = cache_dir.joinpath(
            "node_modules", ".bin",
        ).resolve()
        # Add it to the path. Do not resolve because it might be an exec symlink
        with dffml.prepend_to_path(*node_modules_bin_path.parts, env):
            pass
        return node_modules_bin_path.joinpath("npm-groovy-lint")


class _JAVA_USE_DEFAULT_PLATFORM_URLS:
    pass


class _JAVA_USE_DEFAULT_CACHE_DIR:
    pass


JavaBinary = NewType("JavaBinary", str)
JavaCacheDir = NewType("JavaCacheDir", str)
JavaPlatformURLs = NewType("JavaPlatformURLs", str)


JAVA_USE_DEFAULT_CACHE_DIR = _JAVA_USE_DEFAULT_CACHE_DIR()
JAVA_DEFAULT_CACHE_DIR_PARTS = (
    ".tools", "open-architecture", "innersource", ".cache", "java",
)
JAVA_USE_DEFAULT_PLATFORM_URLS = _JAVA_USE_DEFAULT_PLATFORM_URLS()
JAVA_DEFAULT_PLATFORM_URLS = {
    "Linux": {
        "url": "https://download.java.net/java/GA/jdk19.0.1/afdd2e245b014143b62ccb916125e3ce/10/GPL/openjdk-19.0.1_linux-x64_bin.tar.gz",
        "expected_hash": "ec79c3f085c295876f96d38bfaece0c565ff89152928d71a8b6bf1baf9eda2f27ce6cd857612a4e73540e67c1c0229b5",
    },
}


# TODO Move these ensure_ functions into which can then be overlayed as desired
# via CLI or via install of ad-hoc blank package with only entry_points.txt to
# enable them as desired.
# alice_test.shouldi.contribute.bom_v0_0_0
# This is our reference flow, which knows how to understand, analyize, work in,
# and rebuild itself from anywhere. This allows us to get developers developing
# on alice, or any overlays to alice (being anything else you need to work on or
# analyze). We communicate via ATProto threads to post replys with verifiable
# credentials where the crendential manifest had a SCITT receipt which itself
# appears in a SCITT thread, where the root is the root of trust for that SCITT
# instance.
# IN PROGRESS XXX We are now going to try enabling this as an overlay.
# If this works we'll create a seperate package to enable these for the install.
# Or maybe we'll do a service dev command to create the package ad-hoc.
async def ensure_java(
    cache_dir: JavaCacheDir = JAVA_USE_DEFAULT_CACHE_DIR,
    platform_urls: JavaPlatformURLs = JAVA_USE_DEFAULT_PLATFORM_URLS,
    *,
    env: dict = None,
    logger: logging.Logger = None,
) -> JavaBinary:
    # Download via given platform to download mapping or use default
    if platform_urls is JAVA_USE_DEFAULT_PLATFORM_URLS:
        platform_urls = JAVA_DEFAULT_PLATFORM_URLS
    # Store in given cache directory or create default relative to cwd
    if cache_dir is JAVA_USE_DEFAULT_CACHE_DIR:
        cache_dir = pathlib.Path(*JAVA_DEFAULT_CACHE_DIR_PARTS)
    # Download node
    java_install_path = await dffml.cached_download_unpack_archive(
        **{
            "file_path": cache_dir.joinpath("java.tar.gz"),
            "directory_path": cache_dir.joinpath("java-download"),
            # Use whatever values are appropriate for the system we are on
            **platform_urls[platform.system()],
        }
    )
    # Find the binary
    java_bin_path = [
        path.parent
        for path in java_install_path.rglob("java")
        if path.parent.name == "bin"
    ][0]
    with dffml.prepend_to_path(java_bin_path, env):
        pass
    return java_bin_path.joinpath("java")


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
