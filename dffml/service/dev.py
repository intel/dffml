import os
import sys
import ast
import json
import pydoc
import shutil
import asyncio
import pathlib
import getpass
import tempfile
import importlib
import subprocess
import contextlib
import configparser
import pkg_resources
import unittest.mock
import urllib.request
import importlib.util
from pathlib import Path

from ..base import BaseConfig
from ..util.os import chdir, MODE_BITS_SECURE
from ..version import VERSION
from ..util.skel import Skel, SkelTemplateConfig
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..util.entrypoint import load
from ..base import MissingConfig
from ..util.packaging import is_develop
from ..util.data import traverse_config_get
from ..df.types import Input, DataFlow
from ..df.memory import MemoryOrchestrator
from ..configloader.configloader import BaseConfigLoader
from ..configloader.json import JSONConfigLoader
from ..operation.output import GetSingle

config = configparser.ConfigParser()
config.read(Path("~", ".gitconfig").expanduser())

USER = "unknown"
with contextlib.suppress(KeyError):
    USER = getpass.getuser()

NAME = config.get("user", "name", fallback="Unknown")
EMAIL = config.get("user", "email", fallback="unknown@example.com")

CORE_PLUGINS = [
    ("configloader", "yaml"),
    ("configloader", "png"),
    ("model", "tensorflow"),
    ("model", "scratch"),
    ("model", "scikit"),
    ("model", "tensorflow_hub"),
    ("model", "transformers"),
    ("examples", "shouldi"),
    ("feature", "git"),
    ("feature", "auth"),
    ("service", "http"),
    ("source", "mysql"),
]


def create_from_skel(name):
    """
    Copies samples out of skel/ and does re-naming.
    """

    class CreateCMD(CMD):

        skel = Skel()

        arg_user = Arg(
            "-user",
            help=f"Your username (default: {USER})",
            default=USER,
            required=False,
        )
        arg_name = Arg(
            "-name",
            help=f"Your name (default: {NAME})",
            default=NAME,
            required=False,
        )
        arg_email = Arg(
            "-email",
            help=f"Your email (default: {EMAIL})",
            default=EMAIL,
            required=False,
        )
        arg_description = Arg(
            "-description",
            help=f"Description of python package (default: DFFML {name} {{package name}})",
            default=None,
            required=False,
        )
        arg_target = Arg(
            "-target",
            help=f"Directory to put code in (default: same as package name)",
            default=None,
            required=False,
        )
        arg_package = Arg("package", help="Name of python package to create")

        async def run(self):
            # Set description if None
            if not self.description:
                self.description = f"DFFML {name} {self.package}"
            # Set target directory to package name if not given
            if not self.target:
                self.target = self.package
            # Extract
            self.skel.from_template(
                name,
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


class Run(CMD):
    """
    Run a single operation
    """

    arg_operation = Arg("operation", help="Python path to operation")

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


class ListEntrypoints(CMD):

    arg_entrypoint = Arg(
        "entrypoint", help="Entrypoint to list, example: dffml.model"
    )

    async def run(self):
        for entrypoint in pkg_resources.iter_entry_points(self.entrypoint):
            print(f"{entrypoint} -> {entrypoint.dist!r}")


class Entrypoints(CMD):

    _list = ListEntrypoints


class Export(CMD):

    arg_config = Arg(
        "-config",
        help="ConfigLoader to use",
        type=BaseConfigLoader.load,
        default=JSONConfigLoader,
    )
    arg_not_linked = Arg(
        "-not-linked",
        dest="not_linked",
        help="Do not export dataflows as linked",
        default=False,
        action="store_true",
    )
    arg_export = Arg("export", help="Python path to object to export")

    async def run(self):
        async with self.config(BaseConfig()) as configloader:
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


# TODO (p3) Remove production packages. Download full source if not already
# installed in development mode.
class Install(CMD):
    """
    Uninstall production packages and install dffml in development mode.
    """

    arg_user = Arg(
        "-user", "Preform user install", default=False, action="store_true"
    )

    async def run(self):
        main_package = is_develop("dffml")
        if not main_package:
            raise NotImplementedError(
                "Currenty you need to have at least the main package already installed in development mode."
            )
        # Packages fail to install if we run pip processes in parallel
        packages = list(
            map(
                lambda package: Path(*main_package.parts, *package),
                CORE_PLUGINS,
            )
        )
        self.logger.info("Installing %r in development mode", packages)
        cmd = [sys.executable, "-m", "pip", "install"]
        if self.user:
            # --user sometimes fails
            local_path = Path("~", ".local").expanduser().absolute()
            cmd.append(f"--prefix={local_path}")
        for package in packages:
            cmd += ["-e", str(package.absolute())]
        self.logger.debug("Running: %s", " ".join(cmd))
        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.wait()


class SetupPyKWArg(CMD):
    """
    Get a keyword argument from a call to setup in a setup.py file.
    """

    arg_kwarg = Arg("kwarg", help="Keyword argument to write to stdout")
    arg_setup_filepath = Arg("setup_filepath", help="Path to setup.py")

    @staticmethod
    def get_kwargs(setup_filepath: str):
        setup_filepath = Path(setup_filepath)
        setup_kwargs = {}

        def grab_setup_kwargs(**kwargs):
            setup_kwargs.update(kwargs)

        with chdir(str(setup_filepath.parent)):
            spec = importlib.util.spec_from_file_location(
                "setup", str(setup_filepath.parts[-1])
            )
            with unittest.mock.patch(
                "setuptools.setup", new=grab_setup_kwargs
            ):
                setup = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(setup)

        return setup_kwargs

    async def run(self):
        print(self.get_kwargs(self.setup_filepath)[self.kwarg])


class SetupPy(CMD):

    kwarg = SetupPyKWArg


class RepoDirtyError(Exception):
    """
    Raised when a release was attempted but there are uncommited changes
    """


class Release(CMD):
    """
    Release a package (if not already released)
    """

    arg_package = Arg(
        "package", help="Relative path to package to release", type=Path
    )

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


class BumpPackages(CMD):
    """
    Bump all the versions of all the packages and increment the version number
    given.
    """

    arg_skip = Arg(
        "-skip",
        help="Do not increment versions in these packages",
        nargs="+",
        default=[],
        required=False,
    )
    arg_only = Arg(
        "-only",
        help="Only increment versions in these packages",
        nargs="+",
        default=[],
        required=False,
    )
    arg_version = Arg("version", help="Version to increment by")

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
                    "Skipping skel verison file %s", version_file
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
                        "Verison file not in only %s", version_file
                    )
                    continue
                elif name in self.skip:
                    self.logger.debug("Skipping verison file %s", version_file)
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
            self.logger.debug("Updated verison file %s", version_file)


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
