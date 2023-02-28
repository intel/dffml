import logging
from typing import NewType

import dffml

# from .operations import (
from dffml_operations_innersource.operations import (
    RepoDirectory,
    ActionYAMLFileWorkflowUnixStylePath,
)


ActionsValidatorBinary = NewType("ActionsValidatorBinary", str)
ActionsValidatorResult = NewType("ActionsValidatorResult", dict)


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
    >>> import pathlib
    >>> import tempfile
    >>>
    >>> import dffml
    >>> from dffml_operations_innersource.actions_validator import (
    ...     actions_validator,
    ... )
    >>> from alice_test.shouldi.contribute.actions_validator import (
    ...     ensure_actions_validator,
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
    exit_code = -1
    stderr = ""
    items = None
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
            stderr = result.decode()
            logger.debug("Failed validation: %s", stderr)
            # TODO Parse output into dict or data model
            items = stderr
        elif event is dffml.Subprocess.COMPLETED:
            exit_code = result
    return {
        "pass": bool(exit_code == 0),
        "exit_code": exit_code,
        "items": items,
    }
