import copy
import asyncio
import pathlib
import itertools
import traceback
from typing import (
    Dict,
    Any,
)

from ..df.types import (
    Definition,
    Operation,
    DataFlow,
)
from ..df.base import (
    BaseConfig,
    Operation,
    OperationImplementation,
    OperationImplementationContext,
    OperationImplementationNotInstantiated,
    OperationImplementationNotInstantiable,
)

from ..base import config, field
from ..plugins import inpath
from ..util.entrypoint import entrypoint
from ..util.asynchelper import concurrently


@config
class StackStormPythonScriptActionOperationConfig:
    entry_point: pathlib.Path = field("Python action to run")


class StackStormPythonScriptActionOperationImplementationContext(
    OperationImplementationContext
):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Load the Python file as a module
        entry_point = self.parent.config.entry_point
        with chdir(entry_point.parent):
            spec = importlib.util.spec_from_file_location(
                entry_point.stem, entry_point.name
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Find the action to run within the module

            # Run the action
            breakpoint()
        # Return stdout of called process. Inspect the operation output to
        # determine what it should be called.
        # TODO Handle multiple outputs
        return {list(self.parent.op.outputs.keys())[0]: result}


@config
class StackStormLocalShellActionOperationConfig:
    entry_point: pathlib.Path = field("Python action to run")


class StackStormLocalShellActionOperationImplementationContext(
    OperationImplementationContext
):
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # TODO Implement grab stdout and log stderr in run_command()
        # Return stdout of called process. Inspect the operation output to
        # determine what it should be called.
        return {list(self.parent.op.outputs.keys())[0]: output}


class StackStormLocalShellActionOperationImplementation(
    OperationImplementation
):
    r"""
    Examples
    --------
    """

    CONTEXT = StackStormLocalShellActionOperationImplementationContext
    CONFIG = StackStormLocalShellActionOperationConfig


import io
import re
import shutil
import tarfile
import pathlib
import tempfile
import distutils.version

from ..service.dev import Create
from ..util.os import chdir
from ..util.net import sync_urlopen


async def github_latest_tag_archive_url(owner, repository):
    VERSION_REGEX = re.compile(r"v.*[0-9]*\.[0-9]*\.[0-9]*")
    RELEASE_LINK_REGEX = re.compile(r"tag\/v.*[0-9]*\.[0-9]*\.[0-9]*")

    # URL of repo
    url = f"https://github.com/{owner}/{repository}"

    # List of versions available
    versions = []

    # Check out the releases page to see what tags are available
    with sync_urlopen(url + "/releases") as response:
        # Download the page contents
        page = response.read().decode()
        # Find all the tag URLs
        for link in RELEASE_LINK_REGEX.findall(page):
            # Grab the version from the tag URL
            version_string = VERSION_REGEX.findall(link)[0]
            # use distuilts.version to properly sort versions
            versions.append(distutils.version.LooseVersion(version_string))

    # Sort versions (lowest on page, to highest)
    versions = sorted(versions)
    # Pick the latest version
    latest_version = versions[-1]
    # Create the URL for the latest version
    return f"{url}/archive/refs/tags/{latest_version}.tar.gz"


async def github_download_and_extract_archive(
    version_archive_url, target_path
):
    # Make the request for the archive
    # with sync_urlopen(version_archive_url) as response:
    with open("/tmp/a", "rb") as response:
        # Download archive
        archive_fileobj = io.BytesIO(response.read())
        # Create tarfile object
        with tarfile.open(fileobj=archive_fileobj) as tarfileobj:
            # Read members
            members = tarfileobj.getmembers()
            # Skip the first member as that is the top level directory
            for member in members[1:]:
                # Remove the top level directory from the path and create a
                # path object for it within the new Python module directory
                path = pathlib.Path(
                    target_path,
                    *member.name[len(members[0].name) :].split("/"),
                ).resolve()
                # Mitigation for potential path traversal issue
                if not str(path).startswith(str(target_path)):
                    raise ValueError(f"Path traversal {path}")
                # Modify the extraction path
                member.name = str(path.relative_to(target_path))
                # Extract member
                tarfileobj.extract(member, target_path)


async def stackstorm_actions_to_entry_points(path):
    return {
        action_path.stem: action_path.name
        for action_path in path.joinpath("actions").rglob("*.y*ml")
    }


def stackstorm_operation_name_words(import_package_name, name):
    """
    Name of the operation split into words. Returns package_name + operation
    name as list of strings which can be joined to create the name of an
    operation.
    """
    return import_package_name.replace("stackstorm_", "", 1).split(
        "_"
    ) + name.split("_")


def stackstorm_operation_name(import_package_name, action_name):
    """
    Lowercase underscore joined string of ``name_words``.
    """
    return "_".join(
        stackstorm_operation_name_words(import_package_name, action_name)
    )


def stackstorm_opimp_name(import_package_name, action_name):
    return (
        " ".join(
            stackstorm_operation_name_words(import_package_name, action_name)
        )
        .lower()
        .title()
        .replace(" ", "")
    )


async def stackstorm_operations_py(
    import_package_name, actions_to_entry_points
):
    """
    Return Python code for the operations.py file of a StackStorm pack.
    """
    # Create the code for the operations.py file
    return "\n".join(
        [
            "import importlib.resources",
            "",
            "from dffml import stackstorm_create_opimp",
            "",
            "",
        ]
        + [
            f'{stackstorm_opimp_name(import_package_name, name)} = stackstorm_create_opimp("{stackstorm_operation_name(import_package_name, name)}", "{stackstorm_opimp_name(import_package_name, name)}", importlib.resources.read_text(__package__ + ".actions", "{filename}"))'
            for name, filename in actions_to_entry_points.items()
        ]
    )


async def stackstorm_entry_points_txt(
    import_package_name, actions_to_entry_points
):
    """
    Return INI for the entry_points.txt of a StackStorm pack.
    """
    # Create entry_points.txt file containing operations
    config = configparser.ConfigParser()
    config["dffml.operation"] = {}
    for name, filename in actions_to_entry_points.items():
        # Create entry point for opimp
        config["dffml.operation"][
            stackstorm_operation_name(import_package_name, name)
        ] = f"{import_package_name}.operations:{stackstorm_opimp_name(import_package_name, name)}"
    # Write out entry_points.txt
    with io.StringIO() as fileobj:
        config.write(fileobj)
        return fileobj.getvalue()


import configparser
import sys
import subprocess
import dataclasses


@dataclasses.dataclass
class StackStormAction:
    description: str
    enabled: bool
    name: str
    pack: str
    parameters: dict
    runner_type: str

    def op(self, operation_name):
        return Operation(
            name=operation_name,
            inputs={
                name: Definition(name=name, primitive=parameter["type"])
                for name, parameter in self.parameters.items()
            },
            outputs={
                # TODO Corretly define result
                "result": Definition(
                    name=f"{self.name}.result", primitive="string"
                )
            },
        )


@dataclasses.dataclass
class StackStormPythonScriptAction(StackStormAction):
    entry_point: pathlib.Path


@dataclasses.dataclass
class StackStormLocalShellAction(StackStormAction):
    pass


def stackstorm_create_opimp(operation_name, opimp_name, yaml_contents):
    import yaml

    errors = []

    for ActionClass, OpImp in [
        (
            StackStormPythonScriptAction,
            StackStormPythonScriptActionOperationImplementation,
        ),
        (
            StackStormLocalShellAction,
            StackStormLocalShellActionOperationImplementation,
        ),
    ]:
        try:
            action = ActionClass(**yaml.safe_load(yaml_contents))
            return type(
                opimp_name, (OpImp,), {"op": action.op(operation_name)}
            )
        except Exception as error:
            errors.append(error)

    raise Exception(yaml_contents) from errors[-1]


import contextlib


@contextlib.asynccontextmanager
async def stackstorm_pack_to_operations_package(package_name):
    # version_archive_url = await github_latest_tag_archive_url("StackStorm-Exchange", package_name)

    # Create a temporary directory to create the package in
    with tempfile.TemporaryDirectory() as tempdir:
        # Create a package for the operations
        with chdir(tempdir):
            await Create.operations._main(package_name)
        # Name of package in importable form ("-" replaced with "_")
        import_package_name = package_name.replace("-", "_")
        # Directory where the package is stored
        package_path = pathlib.Path(tempdir, package_name)
        # Directory where the Python module code is stored
        module_path = pathlib.Path(tempdir, package_name, import_package_name)
        # Remove skel Python module contents
        shutil.rmtree(module_path)
        # await github_download_and_extract_archive(version_archive_url, target_path)
        await github_download_and_extract_archive("", module_path)
        # Touch an __init__.py file in the root of the Python module
        module_path.joinpath("__init__.py").write_text("")
        module_path.joinpath("actions", "__init__.py").write_text("")
        # Discover actions and make entry points
        actions_to_entry_points = await stackstorm_actions_to_entry_points(
            module_path
        )
        # Write out operations.py
        module_path.joinpath("operations.py").write_text(
            await stackstorm_operations_py(
                import_package_name, actions_to_entry_points
            )
        )
        # Write out entry_points.txt
        package_path.joinpath("entry_points.txt").write_text(
            await stackstorm_entry_points_txt(
                import_package_name, actions_to_entry_points
            )
        )

        # Requirements
        # "https://github.com/StackStorm/st2/archive/master.zip#egg=st2common&subdirectory=st2common"
        # "https://github.com/StackStorm/st2-rbac-backend/archive/master.zip"

        yield package_path


async def stackstorm_install_pack(pack_name):
    # Create package from pack
    async with stackstorm_pack_to_operations_package(
        pack_name
    ) as package_path:
        # Install pack
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", str(package_path)]
        )
        # Check that operations work
        subprocess.check_call(
            [
                sys.executable,
                "-c",
                f'import {pack_name.replace("-", "_")}.operations',
            ],
        )


async def stackstorm_test():
    await stackstorm_install_pack("stackstorm-networking_utils")


class StackStormPythonScriptActionOperationImplementation(
    OperationImplementation
):
    r"""
    Examples
    --------

    >>> import asyncio
    >>> import pathlib
    >>> from dffml import *
    >>>
    >>> pathlib.Path("print_hello.py").write_text(
    ...     '''
    ...     import sys
    ...     print(sys.argv[-1])
    ...     '''
    ... )
    44
    >>>
    >>> pathlib.Path("print_hello.yaml").write_text(
    ...     '''
    ...     ---
    ...     name: "print_hello"
    ...     runner_type: "python-script"
    ...     description: "Says hello."
    ...     enabled: true
    ...     entry_point: "print_hello.py"
    ...     parameters:
    ...         word:
    ...             type: "string"
    ...             description: "Word to say hello to."
    ...             required: true
    ...             position: 0
    ...     '''
    ... )
    310
    >>>
    >>> async def main():
    ...     for _ctx, results in run(
    ...         dataflow,
    ...         [
    ...             dffml.Input(
    ...                 value="World",
    ...                 definition=print_hello.op.inputs["word"],
    ...             ),
    ...             dffml.Input(
    ...                 value=print_hello.op.outputs["result"],
    ...                 definition=print_hello.op.inputs["word"],
    ...             ),
    ...         ],
    ...     ):
    ...         print(results)
    >>>
    >>> asyncio.run(stackstorm_test())
    """

    CONTEXT = StackStormPythonScriptActionOperationImplementationContext
    CONFIG = StackStormPythonScriptActionOperationConfig
