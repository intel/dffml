import os
import re
import sys
import ast
import json
import pydoc
import shutil
import asyncio
import pathlib
import getpass
import tempfile
import platform
import functools
import importlib
import itertools
import contextlib
import http.server
import configparser
import socketserver
import pkg_resources
import unittest.mock
import urllib.request
import importlib.util
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from ..util.os import chdir, MODE_BITS_SECURE
from ..version import VERSION
from ..util.skel import Skel, SkelTemplateConfig
from ..util.cli.cmd import CMD
from ..util.entrypoint import load
from ..base import MissingConfig, config as configdataclass, field
from ..util.packaging import is_develop
from ..util.net import cached_download
from ..util.data import traverse_config_get, export
from ..util.subprocess import run_command
from ..df.types import Input, DataFlow
from ..df.memory import MemoryOrchestrator
from ..configloader.configloader import BaseConfigLoader
from ..configloader.json import JSONConfigLoader
from ..operation.output import GetSingle
from ..plugins import (
    CORE_PLUGINS,
    CORE_PLUGIN_DEPS,
    PACKAGE_NAMES_TO_DIRECTORY,
    PACKAGE_DIRECTORY_TO_NAME,
)

config = configparser.ConfigParser()
config.read(Path("~", ".gitconfig").expanduser())

USER = "unknown"
with contextlib.suppress(KeyError):
    USER = getpass.getuser()

NAME = config.get("user", "name", fallback="Unknown")
EMAIL = config.get("user", "email", fallback="unknown@example.com")

REPO_ROOT = pathlib.Path(__file__).parents[2]


async def get_cmd_output(cmd: List[str]):
    print(f"$ {' '.join(cmd)}")

    proc = await asyncio.create_subprocess_shell(
        " ".join(cmd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=REPO_ROOT,
    )
    await proc.wait()
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr)
    output = stdout.decode().strip()
    return output


def create_from_skel(plugin_type):
    """
    Copies samples out of skel/ and does re-naming.
    """

    @configdataclass
    class CreateCMDConfig:
        package: str = field("Name of python package to create")
        user: str = field(f"Your username (default: {USER})", default=USER)
        name: str = field(
            f"Your name (default: {NAME})", default=NAME,
        )
        email: str = field(
            f"Your email (default: {EMAIL})", default=EMAIL,
        )
        description: str = field(
            f"Description of python package (default: DFFML {plugin_type} {{package name}})",
            default=None,
        )
        target: str = field(
            f"Directory to put code in (default: same as package name)",
            default=None,
        )

    class CreateCMD(CMD):

        skel = Skel()

        CONFIG = CreateCMDConfig

        async def run(self):
            # Set description if None
            if not self.description:
                self.description = f"DFFML {plugin_type} {self.package}"
            # Set target directory to package name if not given
            if not self.target:
                self.target = self.package
            # Extract
            self.skel.from_template(
                plugin_type,
                self.target,
                SkelTemplateConfig(
                    org=self.user,
                    package=self.package,
                    description=self.description,
                    name=self.name,
                    email=self.email,
                    dffml_version=VERSION,
                ),
            )
            # Create git repo. Required for setuptools_scm version
            for cmd in [
                ["git", "init"],
                ["git", "add", "-A"],
                ["git", "commit", "-snm", "housekeeping: Initial Commit"],
            ]:
                await run_command(
                    cmd, logger=self.logger, cwd=str(self.target)
                )

    return CreateCMD


class Create(CMD):
    """
    Create new models, operations, etc.
    """

    model = create_from_skel("model")
    operations = create_from_skel("operations")
    service = create_from_skel("service")
    source = create_from_skel("source")
    config = create_from_skel("config")


class Link(CMD):
    """
    Create required symlinks from skel/common to the other template directories
    """

    skel = Skel()

    async def run(self):
        for plugin in self.skel.plugins():
            self.skel.create_symlinks(plugin)


class Skeleton(CMD):
    """
    Work with the skeleton directories (create service templates)
    """

    link = Link


@configdataclass
class RunConfig:
    operation: str = field("Python path to operation")


class Run(CMD):
    """
    Run a single operation
    """

    CONFIG = RunConfig

    async def run(self):
        # Push current directory into front of path so we can run things
        # relative to where we are in the shell
        sys.path.insert(0, os.getcwd())
        # Lookup
        modname, qualname_separator, qualname = self.operation.partition(":")
        obj = importlib.import_module(modname)
        if qualname_separator:
            for attr in qualname.split("."):
                obj = getattr(obj, attr)
                self.logger.debug("Loaded operation: %s(%s)", attr, obj)
                return await self.run_op(attr, obj)

    def config_get(self, op, key, definition):
        # TODO De-duplicate code from dffml/base.py
        try:
            value = traverse_config_get(self.extra_config, key)
        except KeyError as error:
            raise MissingConfig("%s missing %s" % (op.name, key))
        # TODO Argparse nargs and Arg and primitives need to be unified
        if "Dict" in definition.primitive:
            # TODO handle Dict / spec completely
            self.logger.critical(
                "Dict / spec'd arguments are not yet completely handled"
            )
            value = json.loads(value[0])
        else:
            typecast = pydoc.locate(
                definition.primitive.replace("List[", "").replace("]", "")
            )
            # TODO This is a oversimplification of argparse's nargs
            if definition.primitive.startswith("List["):
                value = list(map(typecast, value))
            else:
                value = typecast(value[0])
                if typecast is str and value in ["True", "False"]:
                    raise MissingConfig("%s missing %s" % (op.name, key))
        return value

    async def run_op(self, name, opimp):
        # Create an instance of BaseConfigurable and have it parse the inputs
        # from self.extra_config. Use the op.inputs to know what we should pass
        # to config_get
        inputs = []
        for name, definition in opimp.op.inputs.items():
            try:
                inputs.append(
                    Input(
                        value=self.config_get(opimp.op, name, definition),
                        definition=definition,
                    )
                )
            except MissingConfig as error:
                error.args = (f"{opimp.op.inputs}: {error.args[0]}",)
                raise error

        config = {}
        extra_config = self.extra_config

        for i in range(0, 2):
            if "config" in extra_config and len(extra_config["config"]):
                extra_config = extra_config["config"]

        # TODO(p0) This only goes one level deep. This won't work for
        # configs that are multi-leveled
        if extra_config:
            config = extra_config

        dataflow = DataFlow.auto(GetSingle, opimp)
        if config:
            dataflow.configs[opimp.op.name] = config

        # Run the operation in the memory orchestrator
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            # Orchestrate the running of these operations
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(
                    [
                        Input(
                            value=[
                                definition.name
                                for definition in opimp.op.outputs.values()
                            ],
                            definition=GetSingle.op.inputs["spec"],
                        ),
                        *inputs,
                    ]
                ):
                    return results


@configdataclass
class ListEntrypointsConfig:
    entrypoint: str = field("Entrypoint to list, example: dffml.model")


class ListEntrypoints(CMD):

    CONFIG = ListEntrypointsConfig

    async def run(self):
        for entrypoint in pkg_resources.iter_entry_points(self.entrypoint):
            print(f"{entrypoint} -> {entrypoint.dist!r}")


class Entrypoints(CMD):

    _list = ListEntrypoints


@configdataclass
class ExportConfig:
    export: str = field("Python path to object to export",)
    configloader: BaseConfigLoader = field(
        "ConfigLoader to use", default=JSONConfigLoader,
    )
    not_linked: bool = field(
        "Do not export dataflows as linked",
        default=False,
        action="store_true",
    )


class Export(CMD):

    CONFIG = ExportConfig

    async def run(self):
        async with self.configloader() as configloader:
            async with configloader() as loader:
                for obj in load(self.export, relative=os.getcwd()):
                    self.logger.debug("Loaded %s: %s", self.export, obj)
                    if isinstance(obj, DataFlow):
                        sys.stdout.buffer.write(
                            await loader.dumpb(
                                obj.export(linked=not self.not_linked)
                            )
                        )
                    elif hasattr(obj, "export"):
                        sys.stdout.buffer.write(
                            await loader.dumpb(obj.export())
                        )
                    elif hasattr(obj, "_asdict"):
                        sys.stdout.buffer.write(
                            await loader.dumpb(obj._asdict())
                        )
                    else:
                        sys.stdout.buffer.write(
                            await loader.dumpb(export(obj))
                        )


class MissingDependenciesError(Exception):
    """
    Raised when a package has non-pip installable dependencies, or pip
    installable dependencies that must be installed before running the setup.py
    """


@configdataclass
class InstallConfig:
    skip: List[str] = field(
        "List of plugin paths not to install (Example: model/scikit)",
        default_factory=lambda: [],
    )
    nocheck: bool = field(
        "Do not perform pre-install dependency checks", default=False
    )
    user: bool = field(
        "Perform user install", default=False, action="store_true"
    )


# TODO (p3) Remove production packages. Download full source if not already
# installed in development mode.
class Install(CMD):
    """
    Uninstall production packages and install dffml in development mode.
    """

    CONFIG = InstallConfig

    @staticmethod
    def dep_check(
        plugin_deps: Dict[Tuple[str, str], Dict[str, Callable[[], bool]]],
        skip: Optional[List[Tuple[str, str]]] = None,
    ):
        """
        Check if all dependencies are installed prior to running setup.py
        installs of plugins
        """
        if skip is None:
            skip = []
        missing_deps = {}
        for package, deps in plugin_deps.items():
            plugin_path = "/".join(package)
            if plugin_path in skip:
                continue
            missing_plugin_deps = {
                name: check_if_dep_found()
                for name, check_if_dep_found in deps.items()
            }
            if not all(missing_plugin_deps.values()):
                missing_deps[plugin_path] = [
                    name
                    for name, found in missing_plugin_deps.items()
                    if not found
                ]
        # Display info on missing dependencies if there are any
        if missing_deps:
            msg = "The following plugins have unmet dependencies and could not be installed\n\n"
            for plugin_path, deps in missing_deps.items():
                msg += f"    {plugin_path}\n\n"
                for name in deps:
                    msg += f"        {name}\n"
                msg += "\n"
            msg += "Install missing dependencies and re-run plugin install, or skip with\n\n"
            msg += "    -skip "
            msg += " ".join(missing_deps.keys())
            raise MissingDependenciesError(msg)

    async def run(self):
        main_package = is_develop("dffml")
        if not main_package:
            raise NotImplementedError(
                "Currently you need to have at least the main package already installed in development mode."
            )
        # Check if plugins not in skip list have unmet dependencies
        if not self.nocheck:
            self.dep_check(CORE_PLUGIN_DEPS, self.skip)
        self.logger.info("Installing %r in development mode", CORE_PLUGINS)
        failed = []
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
        ]
        # If on Windows, PyTorch wants us to use a find links URL for pip
        if platform.system() == "Windows":
            cmd += ["-f", "https://download.pytorch.org/whl/torch_stable.html"]
        # Install user site directory
        if self.user:
            cmd.append(f"--user")
        for package in CORE_PLUGINS:
            if "/".join(package) in self.skip:
                continue
            package_path = Path(*main_package.parts, *package)
            # Install package in development mode
            cmd += ["-e", str(package_path.absolute()) + "[dev]"]
        self.logger.debug("Running: %s", " ".join(cmd))
        # Packages fail to install if we run pip processes in parallel
        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.wait()
        if proc.returncode != 0:
            importlib.invalidate_caches()
            for package_name, package in PACKAGE_NAMES_TO_DIRECTORY.items():
                try:
                    importlib.util.find_spec(package_name.replace("-", "_"))
                except ModuleNotFoundError:
                    failed.append("/".join(package))
            raise RuntimeError(f"pip failed to install: {','.join(failed)}")


@configdataclass
class SetupPyKWArgConfig:
    kwarg: str = field("Keyword argument to write to stdout")
    setupfilepath: str = field("Path to setup.py",)


class SetupPyKWArg(CMD):
    """
    Get a keyword argument from a call to setup in a setup.py file.
    """

    CONFIG = SetupPyKWArgConfig

    @staticmethod
    def get_kwargs(setupfilepath: str):
        setupfilepath = Path(setupfilepath)
        setup_kwargs = {}

        def grab_setup_kwargs(**kwargs):
            setup_kwargs.update(kwargs)

        with chdir(str(setupfilepath.parent)):
            spec = importlib.util.spec_from_file_location(
                "setup", str(setupfilepath.parts[-1])
            )
            with unittest.mock.patch(
                "setuptools.setup", new=grab_setup_kwargs
            ):
                setup = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(setup)

        return setup_kwargs

    async def run(self):
        print(self.get_kwargs(self.setupfilepath)[self.kwarg])


class VersionNotFoundError(Exception):
    """
    Raised when a version.py file is parsed and no VERSION variable is found.
    """


@configdataclass
class SetupPyVersionConfig:
    versionfilepath: str = field("Path to version.py")


class SetupPyVersion(CMD):
    """
    Read a version.py file that would be referenced by a setup.py or setup.cfg.
    The version.py file contains the version of the package in the VERSION
    variable.
    """

    CONFIG = SetupPyVersionConfig

    def parse_version(self, filename: str):
        self.logger.debug("Checking for VERSION in file %r", filename)
        with open(filename, "r") as f:
            for line in f:
                self.logger.debug("Checking for VERSION in line %r", line)
                if line.startswith("VERSION"):
                    return ast.literal_eval(
                        line.strip().split("=")[-1].strip()
                    )
        raise VersionNotFoundError(self.versionfilepath)

    async def run(self):
        print(self.parse_version(self.versionfilepath))


# Instance of parse_version method as function for logging
parse_version = SetupPyVersion().parse_version


class SetupPy(CMD):

    kwarg = SetupPyKWArg
    version = SetupPyVersion


class RepoDirtyError(Exception):
    """
    Raised when a release was attempted but there are uncommitted changes
    """


@configdataclass
class ReleaseConfig:
    package: Path = field("Relative path to package to release",)


class Release(CMD):
    """
    Release a package (if not already released)
    """

    CONFIG = ReleaseConfig

    async def run(self):
        # Ensure we have a pathlib.Path object
        self.package = Path(self.package).resolve()
        # Ensure target plugin directory has no unstaged changes
        cmd = ["git", "status", "--porcelain", str(self.package)]
        self.logger.debug("Running: %s", " ".join(cmd))
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stderr or proc.returncode != 0:
            raise RuntimeError(stderr.decode())
        if stdout:
            raise RepoDirtyError("Uncommitted changes")
        # cd to directory
        with chdir(str(self.package)):
            # Get name
            # TODO(2ndparty) This needs to change to support second party
            # plugins
            name = {(): "dffml", **PACKAGE_DIRECTORY_TO_NAME,}[
                self.package.relative_to(REPO_ROOT).parts
            ]
            # Load version
            version = parse_version(
                str(self.package / name.replace("-", "_") / "version.py")
            )
            # Check if version is on PyPi
            url = f"https://pypi.org/pypi/{name}/json"
            # TODO(p5) Blocking request in coroutine
            with urllib.request.urlopen(url) as resp:
                package_json = json.load(resp)
                if package_json["info"]["version"] == version:
                    print(f"Version {version} of {name} already on PyPi")
                    return
            # Create a fresh copy of the codebase to upload
            with tempfile.TemporaryDirectory() as tempdir:
                # The directory where the fresh copy will live
                clean_dir = pathlib.Path(tempdir, "clean")
                clean_dir.mkdir(mode=MODE_BITS_SECURE)
                archive_file = pathlib.Path(tempdir, "archive.tar")
                # Create the archive
                with open(archive_file, "wb") as archive:
                    cmd = ["git", "archive", "--format=tar", "HEAD"]
                    print(f"$ {' '.join(cmd)}")
                    proc = await asyncio.create_subprocess_exec(
                        *cmd, stdout=archive
                    )
                    await proc.wait()
                    if proc.returncode != 0:
                        raise RuntimeError
                # Change directory into the clean copy
                with chdir(clean_dir):
                    # Extract the archive
                    shutil.unpack_archive(archive_file)
                    # Upload if not present
                    for cmd in [
                        [sys.executable, "setup.py", "sdist"],
                        [sys.executable, "setup.py", "bdist_wheel"],
                        [sys.executable, "-m", "twine", "upload", "dist/*"],
                    ]:
                        print(f"$ {' '.join(cmd)}")
                        proc = await asyncio.create_subprocess_exec(*cmd)
                        await proc.wait()
                        if proc.returncode != 0:
                            raise RuntimeError


class BumpInter(CMD):
    """
    Bump the version number of other plugins within the dependency list of
    each plugin. This is for interdependent plugins.
    """

    async def run(self):
        # Map package names to their versions
        package_name_to_version = {
            name: (
                re.compile(
                    name + r">=[0-9]+\.[0-9]+\..*$", flags=re.MULTILINE
                ),
                parse_version(
                    REPO_ROOT.joinpath(
                        *directory, name.replace("-", "_"), "version.py"
                    )
                ),
            )
            for directory, name in {
                ".": "dffml",
                **PACKAGE_DIRECTORY_TO_NAME,
            }.items()
        }
        # Go through each plugin
        for directory, name in PACKAGE_DIRECTORY_TO_NAME.items():
            # Update all the setup.cfg files
            setup_cfg_path = REPO_ROOT.joinpath(*directory, "setup.cfg")
            setup_cfg_contents = setup_cfg_path.read_text()
            # Go through each plugin, check if it exists within the setup.cfg
            for name, (regex, version) in package_name_to_version.items():
                update_to = f"{name}>={version}"
                setup_cfg_contents, number_of_subs_made = regex.subn(
                    update_to, setup_cfg_contents
                )
                if number_of_subs_made:
                    self.logger.debug(
                        f"Updated {setup_cfg_path} to use {update_to}"
                    )
            # If it does, overwrite the old version with the new version
            setup_cfg_path.write_text(setup_cfg_contents)


class RCMissingHyphen(Exception):
    pass


@configdataclass
class BumpPackagesConfig:
    version: str = field("Version to increment by",)
    skip: List[str] = field(
        "Do not increment versions in these packages",
        default_factory=lambda: [],
        required=False,
    )
    only: List[str] = field(
        "Only increment versions in these packages",
        default_factory=lambda: [],
        required=False,
    )


class BumpPackages(CMD):
    """
    Bump all the versions of all the packages and increment the version number
    given.
    """

    CONFIG = BumpPackagesConfig

    @staticmethod
    def bump_version(original, increment):
        # Ensure that we conform to semantic versioning spec. PEP-440 will
        # normalize it to not have a hyphen.
        if "rc" in original and not "-rc" in original:
            raise RCMissingHyphen(
                f"Semantic versioning requires a hyphen, original is in violation {original}"
            )
        if "rc" in increment and not "-rc" in increment:
            raise RCMissingHyphen(
                f"Semantic versioning requires a hyphen, increment is in violation {increment}"
            )
        # Support for release candidates X.Y.Z-rcN
        # Parse out the release candidate if it exists
        original_rc = 0
        if "-rc" in original:
            original, original_rc = original.split("-rc")
            original_rc = int(original_rc)
        increment_rc = None
        if "-rc" in increment:
            increment, increment_rc = increment.split("-rc")
            increment_rc = int(increment_rc)
        # Split on .
        # zip: Create three instances of (original[i], increment[i])
        new_version_no_rc_numbers = []
        for n_original, n_increment in zip(
            original.split("."), increment.split(".")
        ):
            if n_increment == "Z":
                # If 'Z' was given as the increment, zero spot instead of sum
                new_version_no_rc_numbers.append(0)
            else:
                # Add each pair together
                new_version_no_rc_numbers.append(
                    int(n_original) + int(n_increment)
                )
        # map: str: Convert back to strings
        # Join numbers with .
        new_version_no_rc = ".".join(map(str, new_version_no_rc_numbers))
        # Do not add rc if it wasn't incremented
        if increment_rc is None:
            return new_version_no_rc
        # Otherwise, add rc
        return new_version_no_rc + f"-rc{original_rc + increment_rc}"

    async def run(self):
        main_package = is_develop("dffml")
        if not main_package:
            raise NotImplementedError(
                "Need to reinstall the main package in development mode."
            )
        # Go through each plugin
        for directory, name in {
            ".": "dffml",
            **PACKAGE_DIRECTORY_TO_NAME,
        }.items():
            # Update all the version files
            version_file = REPO_ROOT.joinpath(
                *directory, name.replace("-", "_"), "version.py"
            )
            # If we're only supposed to increment versions of some packages,
            # check we're in the right package, skip if not.
            with chdir(version_file.parents[1]):
                if self.only and name not in self.only:
                    self.logger.debug(
                        "Version file not in only %s", version_file
                    )
                    continue
                elif name in self.skip:
                    self.logger.debug("Skipping version file %s", version_file)
                    continue
            # Read the file
            filetext = version_file.read_text()
            # Find the version as a string
            modified_lines = []
            for line in filetext.split("\n"):
                # Look for the line containing the version string
                if line.startswith("VERSION"):
                    # Parse the version string
                    version = ast.literal_eval(line.split("=")[-1].strip())
                    # Increment the version string
                    version = self.bump_version(version, self.version)
                    # Modify the line to use the new version string
                    line = f'VERSION = "{version}"'
                # Append line to list of lines to write back
                modified_lines.append(line)
            # Write back the file using the modified lines
            filetext = version_file.write_text("\n".join(modified_lines))
            self.logger.debug("Updated version file %s", version_file)


class RemoveUnusedImports(CMD):
    async def _run_autoflake(self):
        cmd = [
            "git",
            "ls-files",
            "'*.py'",
            "|",
            "xargs",
            "autoflake",
            "--in-place",
            "--remove-all-unused-imports",
            "--ignore-init-module-imports",
        ]
        await get_cmd_output(cmd)

    async def run(self):
        await self._run_autoflake()


class CommitLintError(Exception):
    pass


class LintCommits(CMD):
    """
    Enforce commit message style 
    """

    substitutions = {"shouldi": "examples/shouldi/"}

    def _get_ignore_filter(self):
        return lambda x: not x.endswith("_")

    def _execute_func_list(self, param, func_list):
        for func in func_list:
            param = func(param)
        return param

    def _make_composite_function(self, *func):
        def compose(f, g):
            return lambda x: f(g(x))

        return functools.reduce(compose, func, lambda x: x)

    def _test_mutation(self, x):
        # Conditional mutations like this should
        # behave like no_mutation if condition is
        # not met
        blocks = x.split("/")
        first_block = blocks[0].lower()
        second_block = blocks[1] if len(blocks) >= 3 else None
        if any(
            [
                first_block in "tests",
                second_block in "tests" if second_block is not None else False,
            ]
        ):
            blocks[-1] = "test_" + blocks[-1]
            mutated_msg = "/".join(blocks)
            return mutated_msg
        return x

    def _substitution_mutation(self, x):
        return "/".join([self.substitutions.get(i, i) for i in x.split("/")])

    async def _get_file_mutations(self):
        no_mutation = lambda x: x
        mutation_func_factory = lambda ext: lambda x: x + ext
        extensions = (
            await self._get_all_exts()
            if not hasattr(self, "extensions")
            else self.extensions
        )
        mutations = {
            "prefix_mutations": [
                no_mutation,
                lambda x: "." + x,
                lambda x: "dffml/" + x,
            ],
            "body_mutations": [
                self._make_composite_function(
                    self._substitution_mutation, self._test_mutation
                )
            ],
            "suffix_mutations": [
                no_mutation,
                *[mutation_func_factory(ext) for ext in extensions],
                lambda x: x + "/shouldi",
            ],
        }
        return mutations

    async def _get_relevant_commits(self):
        #! This needs to change when master is renamed to main.
        cmd = ["git", "cherry", "-v", "origin/master"]
        commits = await get_cmd_output(cmd)
        commits_list = [
            " ".join(line.split()[2:]) for line in commits.split("\n")
        ]
        return commits_list

    async def _get_commmit_details(self, msg):
        cmd = ["git", "log", f"""--grep='{msg}'"""]
        commit_details = await get_cmd_output(cmd)
        return commit_details

    async def _get_all_exts(self,):
        cmd = [
            "git",
            "ls-tree",
            "-r",
            "HEAD",
            "--name-only",
        ]
        tracked_files = await get_cmd_output(cmd)
        tracked_files = tracked_files.split("\n")
        extentions = set()
        for file in tracked_files:
            _, file_extension = os.path.splitext(file)
            extentions.add(file_extension)
        return extentions

    async def validate_commit_msg(self, msg):
        root = Path(__file__).parents[2]
        test_path = "/".join(
            filter(
                self._get_ignore_filter(), map(str.strip, msg.split(":")[:-1])
            )
        )
        mutations_dict = await self._get_file_mutations()
        mutation_pipelines = itertools.product(
            *[
                [mutation for mutation in mutations_list]
                for mutations_list in mutations_dict.values()
            ]
        )
        mutated_paths = [
            root / pathlib.Path(self._execute_func_list(test_path, pipeline))
            for pipeline in mutation_pipelines
        ]
        is_valid = any(
            [
                all(
                    [
                        mutated_path.exists(),
                        mutated_path != root,
                        test_path != "",
                    ]
                )
                for mutated_path in mutated_paths
            ]
        )
        return is_valid

    async def run(self):
        self.extensions = await self._get_all_exts()
        commits_list = await self._get_relevant_commits()
        is_valid_lst = [
            await self.validate_commit_msg(msg) for msg in commits_list
        ]
        raise_error = not all(is_valid_lst)
        if raise_error:
            for commit, is_valid in zip(commits_list, is_valid_lst):
                if not is_valid:
                    print(await self._get_commmit_details(commit))
            raise CommitLintError


class CI(CMD):
    """
    CI related commands
    """


class Lint(CMD):
    """
    Linting related commands
    """

    commits = LintCommits
    imports = RemoveUnusedImports


class Bump(CMD):
    """
    Bump the the main package in the versions plugins, or any or all libraries.
    """

    inter = BumpInter
    packages = BumpPackages


class SphinxBuildError(Exception):
    """
    Raised when sphinx-build command exits with a non-zero error code.
    """

    def __str__(self):
        return "[ERROR] Failed run sphinx, is it installed (pip install -U .[dev])?"


@configdataclass
class MakeDocsConfig:
    target: Path = field(
        "Path to target directory for saving docs", default=None
    )
    port: int = field("PORT for the local docs server", default=8080)
    http: bool = field(
        "If set a SimpleHTTP server would be started to show generated docs",
        default=False,
    )
    no_strict: bool = field(
        "If set do not fail on Sphinx warnings", default=False,
    )


class MakeDocs(CMD):
    """
    Generate docs of the complete package 
    """

    CONFIG = MakeDocsConfig

    async def _exec_cmd(self, cmd: List[str]) -> int:
        print(f"$ {' '.join(cmd)}")
        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.wait()
        return proc.returncode

    async def run(self):
        root = Path(__file__).parents[2]
        pages_path = (
            root / "pages" if self.target is None else Path(self.target)
        )
        shutil.rmtree(pages_path, ignore_errors=True)
        pages_path.mkdir()  # needed for testing

        docs_path = root / "docs"
        files_to_check = [
            (("changelog.md",), ("CHANGELOG.md",)),
            (("shouldi.md",), ("examples", "shouldi", "README.md",)),
            (
                ("contributing", "consoletest.md",),
                ("dffml", "util", "testing", "consoletest", "README.md",),
            ),
        ]

        for symlink, source in files_to_check:
            file_path = docs_path.joinpath(*symlink)
            if not file_path.exists():
                file_path.symlink_to(root.joinpath(*source))

        # HTTP Service Docs
        service_path = docs_path / "plugins" / "service"
        service_path.mkdir(parents=True, exist_ok=True)
        http_docs_pth = service_path / "http"

        if http_docs_pth.exists():
            http_docs_pth.unlink()

        http_docs_pth.symlink_to(root / "service" / "http" / "docs")

        # Main Docs
        scripts_path = root / "scripts"
        scripts_to_run = ["docs.py", "docs_api.py"]
        for script in scripts_to_run:
            cmd = [sys.executable, str(scripts_path / script)]
            returncode = await self._exec_cmd(cmd)
            if returncode != 0:
                raise RuntimeError

        cmd = [
            [
                e.name
                for e in pkg_resources.iter_entry_points("console_scripts")
                if e.name.startswith("sphinx-build")
            ][0],
            "-b",
            "html",
            "docs",
            str(pages_path),
        ]
        # Fail on warnings unless -no-strict is given
        if not self.no_strict:
            cmd.insert(1, "-W")
        returncode = await self._exec_cmd(cmd)
        if returncode != 0:
            raise SphinxBuildError

        images_path = docs_path / "images"
        images_set = set(images_path.iterdir())
        target_set = set(pages_path.iterdir())

        files_to_copy = list(images_set - target_set)
        for file in files_to_copy:
            shutil.copy(file, pages_path)

        copybutton_path = pages_path / "_static" / "copybutton.js"

        await cached_download(
            "https://raw.githubusercontent.com/python/python-docs-theme/master/python_docs_theme/static/copybutton.js",
            copybutton_path,
            "061b550f64fb65ccb73fbe61ce15f49c17bc5f30737f42bf3c9481c89f7996d0004a11bf283d6bd26cf0b65130fc1d4b",
        )

        nojekyll_path = pages_path / ".nojekyll"
        nojekyll_path.touch(exist_ok=True)

        if self.http:

            handler = functools.partial(
                http.server.SimpleHTTPRequestHandler, directory=str(pages_path)
            )

            with socketserver.TCPServer(("", self.port), handler) as httpd:
                print(f"http://127.0.0.1:{httpd.server_address[1]}/")
                httpd.serve_forever()


class Develop(CMD):
    """
    Development utilities for hacking on DFFML itself
    """

    create = Create
    skel = Skeleton
    run = Run
    export = Export
    entrypoints = Entrypoints
    install = Install
    release = Release
    setuppy = SetupPy
    bump = Bump
    ci = CI
    lint = Lint
    docs = MakeDocs
