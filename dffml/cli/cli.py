# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Command line interface evaluates packages given their source URLs
"""
import pathlib
import pdb
import sys
import traceback
import contextlib
import subprocess
import pkg_resources
import importlib.util
from typing import Union

from .log import LOGGER
from ..version import VERSION
from ..record import Record
from ..feature.feature import Features
from ..df.types import DataFlow
from ..plugins import PACKAGE_NAMES_BY_PLUGIN, PACKAGE_NAMES_TO_DIRECTORY
from ..source.df import DataFlowSource, DataFlowSourceConfig
from ..source.source import Sources, BaseSource, SubsetSources
from ..configloader.configloader import BaseConfigLoader
from ..util.packaging import is_develop
from ..util.cli.cmd import CMD
from ..util.cli.cmds import (
    SourcesCMD,
    PortCMD,
    KeysCMD,
    KeysCMDConfig,
    PortCMDConfig,
    SourcesCMDConfig,
)
from ..util.config.fields import FIELD_SOURCES
from ..base import field, config

from .dataflow import Dataflow
from .config import Config
from .ml import Train, Accuracy, Predict
from .list import List

version = VERSION


@config
class VersionConfig:
    no_errors: bool = field(
        "Set to ignore errors when loading modules", default=False
    )


class Version(CMD):
    """
    Print version and installed dffml packages
    """

    CONFIG = VersionConfig

    @staticmethod
    async def git_hash(path: Union[pathlib.Path, str]):
        """
        If the path is a git repo we'll return.

        Examples
        --------

        >>> import pathlib
        >>> import asyncio
        >>> import subprocess
        >>>
        >>> import dffml.cli.cli
        >>>
        >>> subprocess.check_call(["git", "init"])
        0
        >>> subprocess.check_call(["git", "config", "user.name", "First Last"])
        0
        >>> subprocess.check_call(["git", "config", "user.email", "first.last@example.com"])
        0
        >>> pathlib.Path("README.md").write_text("Contents")
        8
        >>> subprocess.check_call(["git", "add", "README.md"])
        0
        >>> subprocess.check_call(["git", "commit", "-m", "First commit"])
        0
        >>> dirty, short_hash = asyncio.run(dffml.cli.cli.Version.git_hash("."))
        >>> dirty
        False
        >>> int(short_hash, 16) > 0
        True
        """
        path = pathlib.Path(path).resolve()
        dirty = None
        short_hash = None
        with contextlib.suppress(subprocess.CalledProcessError):
            dirty = bool(
                subprocess.call(
                    ["git", "diff-index", "--quiet", "HEAD", "--"],
                    cwd=str(path),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            )
            short_hash = (
                subprocess.check_output(
                    ["git", "show", "-s", "--pretty=%h %D", "HEAD"],
                    cwd=str(path),
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .split()
            )[0]
        return dirty, short_hash

    async def run(self):
        self.logger.debug("Reporting version")
        # Versions of plugins
        for package_name in ["dffml"] + PACKAGE_NAMES_BY_PLUGIN["all"]:
            version = "not installed"
            path = ""
            import_package_name = package_name.replace("-", "_")
            import_package_name_version = import_package_name + ".version"
            for module_name in [
                import_package_name,
                import_package_name_version,
            ]:
                with contextlib.redirect_stderr(
                    None
                ), contextlib.redirect_stdout(None):
                    try:
                        module = importlib.import_module(module_name)
                    except ModuleNotFoundError:
                        continue
                    except Exception as error:
                        if self.no_errors:
                            self.logger.error(
                                f"Failed to import {module_name}: {traceback.format_exc().rstrip()}"
                            )
                            version = "ERROR"
                            continue
                        else:
                            raise
                    sys.modules[module_name] = module
                if module_name in sys.modules:
                    module = sys.modules[module_name]
                    if module_name.endswith(".version"):
                        version = module.VERSION
                    else:
                        path = module.__path__[0]
                        # Report if code comes from git repo
                        dirty, short_hash = await self.git_hash(path)
            package_details = [package_name, version]
            if path:
                package_details.append(path)
                if dirty is not None and short_hash is not None:
                    package_details.append(short_hash)
                    if dirty:
                        package_details.append("(dirty git repo)")
            print(" ".join(package_details))


class Packages(CMD):
    async def run(self):
        print(
            "\n".join(
                sorted(["dffml"] + list(PACKAGE_NAMES_TO_DIRECTORY.keys()))
            )
        )


@config
class EditCMDConfig:
    dataflow: str = field(
        "File containing exported DataFlow", default=None,
    )
    config: BaseConfigLoader = field(
        "ConfigLoader to use for importing DataFlow", default=None,
    )
    features: Features = field(
        "Feature definitions of records to update",
        required=False,
        default_factory=lambda: [],
    )
    sources: Sources = FIELD_SOURCES


class BaseEditCMD(SourcesCMD):

    CONFIG = EditCMDConfig

    async def __aenter__(self):
        await super().__aenter__()
        if self.dataflow:
            dataflow_path = pathlib.Path(self.dataflow)
            config_cls = self.config
            if config_cls is None:
                config_type = dataflow_path.suffix.replace(".", "")
                config_cls = BaseConfigLoader.load(config_type)
            async with config_cls.withconfig(
                self.extra_config
            ) as configloader:
                async with configloader() as loader:
                    exported = await loader.loadb(dataflow_path.read_bytes())
                self.dataflow = DataFlow._fromdict(**exported)

            self.sources = DataFlowSource(
                DataFlowSourceConfig(
                    source=self.sources,
                    dataflow=self.dataflow,
                    features=self.features,
                )
            )


class EditAllRecords(BaseEditCMD, SourcesCMD):
    """
    Edit all records using operations
    """

    async def run(self):
        async with self.sources as src:
            async with src() as sctx:
                async for record in sctx.records():
                    if not self.dataflow:
                        pdb.set_trace()
                    await sctx.update(record)


@config
class EditRecordConfig(EditCMDConfig, KeysCMDConfig):
    pass


class EditRecord(EditAllRecords, KeysCMD):
    """
    Edit each specified record
    """

    CONFIG = EditRecordConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = SubsetSources(*self.sources, keys=self.keys)


class Edit(CMD):
    """
    Edit records
    """

    _all = EditAllRecords
    record = EditRecord


@config
class MergeConfig:
    src: BaseSource = field(
        "Source to pull records from", labeled=True,
    )
    dest: BaseSource = field(
        "Source to merge records into", labeled=True,
    )


class Merge(CMD):
    """
    Merge record data between sources
    """

    CONFIG = MergeConfig

    async def run(self):
        async with self.src.withconfig(
            self.extra_config
        ) as src, self.dest.withconfig(self.extra_config) as dest:
            async with src() as sctx, dest() as dctx:
                async for src in sctx.records():
                    record = Record(src.key)
                    record.merge(src)
                    record.merge(await dctx.record(record.key))
                    await dctx.update(record)


class ImportExportCMDConfig(PortCMDConfig, SourcesCMDConfig):
    filename: str = field(
        "Filename", default=None,
    )


class ImportExportCMD(PortCMD, SourcesCMD):
    """Shared import export arguments"""

    CONFIG = ImportExportCMDConfig


class Import(ImportExportCMD):
    """Imports records"""

    async def run(self):
        async with self.sources as sources:
            async with sources() as sctx:
                return await self.port.import_from_file(sctx, self.filename)


class Export(ImportExportCMD):
    """Exports records"""

    async def run(self):
        async with self.sources as sources:
            async with sources() as sctx:
                return await self.port.export_to_file(sctx, self.filename)


SERVICES_LOGGER = LOGGER.getChild("services")


def failed_to_load_service(loading_what: str = "services"):
    """
    Sometimes weird dependency issues show up and prevent us from loading
    anything. We log the traceback in that case.
    """
    SERVICES_LOGGER.error(
        "Error while loading %s: %s", loading_what, traceback.format_exc()
    )


def services():
    """
    Loads dffml.services.cli entrypoint and creates a CMD class incorporating
    all of the loaded CLI versions of services as subcommands.
    """

    class Service(CMD):
        """
        Expose various functionalities of dffml
        """

        pass

    try:
        for i in pkg_resources.iter_entry_points("dffml.service.cli"):
            try:
                loaded = i.load()
            except:
                failed_to_load_service(repr(i))
                continue
            if issubclass(loaded, CMD):
                setattr(Service, i.name, loaded)
    except:
        failed_to_load_service()
    return Service


class CLI(CMD):
    """
    CLI interface for dffml
    """

    version = Version
    packages = Packages
    _list = List
    edit = Edit
    merge = Merge
    _import = Import
    export = Export
    train = Train
    accuracy = Accuracy
    predict = Predict
    service = services()
    dataflow = Dataflow
    config = Config
