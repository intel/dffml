# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Command line interface evaluates packages given their source URLs
"""
import pathlib
import pdb
import pkg_resources
import os

from ..version import VERSION
from ..record import Record
from ..feature.feature import Features, Feature
from ..util.cli.parser import list_action
from ..df.types import DataFlow
from ..source.df import DataFlowSource, DataFlowSourceConfig
from ..source.source import Sources, BaseSource, SubsetSources
from ..source.json import JSONSource
from ..source.csv import CSVSource
from ..source.file import FileSourceConfig
from ..util.packaging import is_develop
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD, CMDConfig
from ..util.cli.cmds import (
    SourcesCMD,
    PortCMD,
    KeysCMD,
    PortCMDConfig,
    SourcesCMDConfig,
)
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


class BaseEditCMD(SourcesCMD):
    arg_dataflow = Arg(
        "-dataflow", help="File containing exported DataFlow", required=False,
    )
    arg_config = Arg(
        "-config",
        help="ConfigLoader to use for importing DataFlow",
        required=False,
        type=BaseConfigLoader.load,
        default=None,
    )
    arg_features = Arg(
        "-features",
        help="Feature definitions of records to update",
        required=False,
        default=[],
        type=Feature,
        nargs="+",
        action=list_action(Features),
    )

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


class EditRecord(EditAllRecords, KeysCMD):
    """
    Edit each specified record
    """

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
class MergeConfig(CMDConfig):
    src: BaseSource = field(
        "Sources to pull records from", position=0, labeled=True,
    )
    dest: BaseSource = field(
        "Sources to merge records into", position=1, labeled=True,
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
