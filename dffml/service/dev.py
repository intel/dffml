import os
import re
import sys
import ast
import json
import pydoc
import shutil
import string
import asyncio
import pathlib
import getpass
import tempfile
import importlib
import subprocess
import contextlib
import dataclasses
import configparser
import pkg_resources
import unittest.mock
import urllib.request
import importlib.util
from pathlib import Path
from typing import List, Dict, Tuple, Callable, Optional

from ..base import BaseConfig
from ..util.os import chdir, MODE_BITS_SECURE
from ..version import VERSION
from ..util.skel import Skel, SkelTemplateConfig
from ..util.cli.cmd import CMD
from ..util.entrypoint import load
from ..base import MissingConfig, config as configdataclass, field
from ..util.packaging import is_develop
from ..util.data import traverse_config_get, export
from ..df.types import Input, DataFlow
from ..df.memory import MemoryOrchestrator
from ..configloader.configloader import BaseConfigLoader
from ..configloader.json import JSONConfigLoader
from ..operation.output import GetSingle
from ..plugins import (
    CORE_PLUGINS,
    CORE_PLUGIN_DEPS,
    PACKAGE_NAMES_TO_DIRECTORY,
)

config = configparser.ConfigParser()
config.read(Path("~", ".gitconfig").expanduser())

USER = "unknown"
with contextlib.suppress(KeyError):
    USER = getpass.getuser()

NAME = config.get("user", "name", fallback="Unknown")
EMAIL = config.get("user", "email", fallback="unknown@example.com")


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
        "Do not preform pre-install dependency checks", default=False
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
                "Currenty you need to have at least the main package already installed in development mode."
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
        # Install to prefix, since --user sometimes fails
        if self.user:
            local_path = Path("~", ".local").expanduser().absolute()
            cmd.append(f"--prefix={local_path}")
        for package in CORE_PLUGINS:
            if "/".join(package) in self.skip:
                continue
            package_path = Path(*main_package.parts, *package)
            # Install package in development mode
            cmd += ["-e", str(package_path.absolute())]
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


class SetupPy(CMD):

    kwarg = SetupPyKWArg
    version = SetupPyVersion


class RepoDirtyError(Exception):
    """
    Raised when a release was attempted but there are uncommited changes
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
            raise RepoDirtyError("Uncommited changes")
        # cd to directory
        with chdir(str(self.package)):
            # Load version
            setup_kwargs = SetupPyKWArg.get_kwargs(
                os.path.join(os.getcwd(), "setup.py")
            )
            name = setup_kwargs["name"]
            version = setup_kwargs["version"]
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


class BumpMain(CMD):
    """
    Bump the version number of the main package within the dependency list of
    each plugin.
    """

    async def run(self):
        main_package = is_develop("dffml")
        if not main_package:
            raise NotImplementedError(
                "Need to reinstall the main package in development mode."
            )
        # TODO Implement this in Python
        proc = await asyncio.create_subprocess_exec(
            "bash", str(pathlib.Path(main_package, "scripts", "bump_deps.sh"))
        )
        await proc.wait()
        if proc.returncode != 0:
            raise RuntimeError


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
        # Split on .
        # map: int: Convert to an int
        # zip: Create three instances of (original[i], increment[i])
        # map: sum: Add each pair together
        # map: str: Convert back to strings
        return ".".join(
            map(
                str,
                map(
                    sum,
                    zip(
                        map(int, original.split(".")),
                        map(int, increment.split(".")),
                    ),
                ),
            )
        )

    async def run(self):
        main_package = is_develop("dffml")
        if not main_package:
            raise NotImplementedError(
                "Need to reinstall the main package in development mode."
            )
        main_package = pathlib.Path(main_package)
        skel = main_package / "dffml" / "skel"
        version_files = map(
            lambda path: pathlib.Path(*path.split("/")).resolve(),
            filter(
                bool,
                subprocess.check_output(["git", "ls-files", "*/version.py"])
                .decode()
                .split("\n"),
            ),
        )
        # Update all the version files
        for version_file in version_files:
            # Ignore skel
            if skel in version_file.parents:
                self.logger.debug(
                    "Skipping skel version file %s", version_file
                )
                continue
            # If we're only supposed to increment versions of some packages,
            # check we're in the right package, skip if not.
            setup_filepath = version_file.parent.parent / "setup.py"
            with chdir(setup_filepath.parent):
                try:
                    name = SetupPyKWArg.get_kwargs(setup_filepath)["name"]
                except Exception as error:
                    raise Exception(setup_filepath) from error
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


@configdataclass
class PinDepsConfig:
    logs: pathlib.Path = field("Path to log file for main plugin")
    update: bool = field(
        "Update all requirements.txt files with pinned dependneices",
        default=False,
    )


@dataclasses.dataclass
class PinDepsPlugin:
    path: str
    requirements_txt_path: pathlib.Path
    requirements_txt_contents: str
    requirements_txt_pinned: str


class PinDeps(CMD):
    """
    Parse a GitHub Actions log archive to produce pinned dependencies for each
    requirements.txt
    """

    CONFIG = PinDepsConfig
    # Lowest supported version of Python by all plugins
    LOWEST_PYTHON_VERSION = (3, 7)

    @classmethod
    def requirement_package_name(cls, line):
        """
        Parse a line from requirements.txt and return the package name

        "Per PEP 508, valid project names must: Consist only of ASCII letters,
        digits, underscores (_), hyphens (-), and/or periods (.), and. Start & end
        with an ASCII letter or digit."
        """
        if not line:
            raise ValueError("line is blank")

        i = 0
        name = ""
        while i < len(line) and line[i] in (
            "_",
            "-",
            ".",
            *string.ascii_letters,
            *string.digits,
        ):
            name += line[i]
            i += 1

        # Replace _ with - since that's what PyPi uses
        return name.replace("_", "-")

    @classmethod
    def remove_ansi_escape(cls, contents):
        """
        Found on Stack Overflow from Martijn Pieters, only modified input variable
        name.
        - https://stackoverflow.com/a/14693789
        - https://creativecommons.org/licenses/by-sa/4.0/
        """
        # 7-bit and 8-bit C1 ANSI sequences
        ansi_escape_8bit = re.compile(
            br"(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])"
        )
        return ansi_escape_8bit.sub(b"", contents)

    @classmethod
    def parse_github_actions_log_file(cls, contents):
        lines = (
            cls.remove_ansi_escape(contents)
            .replace(b"\r", b"")
            .decode(errors="ignore")
            .split("\n")
        )

        # Map packages to versions that were installed in CI
        ci_installed = {}

        for line in lines:
            if "Requirement already satisfied:" in line:
                # Check for packages that may have been installed previously that would show
                # up as file:// URLs
                # Example:
                #   Requirement already satisfied: vowpalwabbit>=8.8.1 in /usr/share/miniconda/lib/python3.7/site-packages (from dffml-model-vowpalWabbit==0.0.1) (8.8.1)
                line = line.split()
                # Get package name
                package_name = cls.requirement_package_name(
                    line[line.index("satisfied:") + 1]
                )
                if not package_name:
                    continue
                # Check if we don't have a version for this package yet
                if package_name not in ci_installed:
                    # Get package version, strip ()
                    ci_installed[package_name] = line[-1][1:-1]
            elif "==" in line:
                # Skip any lines that are not in the format of:
                #   2020-11-23T05:54:36.4861610Z absl-py==0.11.0
                if line.count("Z ") != 1:
                    continue
                line = line.split("Z ")[-1].split("==")
                if not line[0] or not line[1]:
                    continue
                # Get package name
                package_name = cls.requirement_package_name(line[0])
                if not package_name:
                    continue
                # with contextlib.suppress(Exception):
                ci_installed[package_name] = line[1]

        return ci_installed

    async def pin_deps(self, contents: bytes):
        if not b"PLUGIN=" in contents:
            return

        root = pathlib.Path(__file__).parents[2]

        ci_installed = self.parse_github_actions_log_file(contents)

        for requirements_txt_path in root.rglob("requirements.txt"):
            self.logger.debug(requirements_txt_path)
            requirements_txt_contents = requirements_txt_path.read_text()
            modify_contents = requirements_txt_contents.split("\n")
            # Add all packages in requirements files to set of required
            # packages
            for i, line in enumerate(modify_contents):
                # Skip comments
                if line.strip().startswith("#") or not line:
                    continue
                package_name = self.requirement_package_name(line)
                if not package_name:
                    continue
                # Ensure package was installed in CI
                if not package_name in ci_installed:
                    raise ValueError(
                        f"Plugin {requirements_txt_path.parent}: {package_name!r} not in {ci_installed}"
                    )
                # Modify the line to be a pinned package
                modify_contents[i] = (
                    package_name + "==" + ci_installed[package_name]
                )

                self.logger.debug(f"{line:<40} | {modify_contents[i]}")

            yield PinDepsPlugin(
                path=str(requirements_txt_path.relative_to(root)),
                requirements_txt_path=requirements_txt_path,
                requirements_txt_contents=requirements_txt_contents,
                requirements_txt_pinned="\n".join(modify_contents),
            )

    async def run(self):
        async for plugin in self.pin_deps(
            pathlib.Path(self.logs).read_bytes()
        ):
            if self.update:
                plugin.requirements_txt_path.write_text(
                    plugin.requirements_txt_pinned
                )


class CI(CMD):
    """
    CI related commands
    """

    pindeps = PinDeps


class Bump(CMD):
    """
    Bump the the main package in the versions plugins, or any or all libraries.
    """

    main = BumpMain
    packages = BumpPackages


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
