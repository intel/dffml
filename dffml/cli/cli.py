# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Command line interface evaluates packages given their source URLs
"""
import pathlib
import pdb
import pkg_resources

from ..version import VERSION
from ..record import Record
from ..feature.feature import Features
from ..df.types import DataFlow
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


class Version(CMD):
    """
    Print version and installed dffml packages
    """

    async def run(self):
        self.logger.debug("Reporting version")
        devmode = is_develop("dffml")
        print(f"dffml version {VERSION} (devmode: {str(devmode)})")


@config
class EditCMDConfig:
    dataflow: str = field("File containing exported DataFlow",)
    config: BaseConfigLoader = field(
        "ConfigLoader to use for importing DataFlow",
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

    for i in pkg_resources.iter_entry_points("dffml.service.cli"):
        loaded = i.load()
        if issubclass(loaded, CMD):
            setattr(Service, i.name, loaded)
    return Service


class CLI(CMD):
    """
    CLI interface for dffml
    """

    version = Version
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
