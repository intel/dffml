# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Command line interface evaluates packages given their source URLs
"""
import pdb
import pkg_resources

from ..version import VERSION
from ..record import Record
from ..source.source import BaseSource
from ..util.packaging import is_develop
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..util.cli.cmds import SourcesCMD, PortCMD, KeysCMD

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


class Edit(SourcesCMD, KeysCMD):
    """
    Edit each specified record
    """

    async def run(self):
        async with self.sources as sources:
            async with sources() as sctx:
                for key in self.keys:
                    record = await sctx.record(key)
                    pdb.set_trace()
                    await sctx.update(record)


class Merge(CMD):
    """
    Merge record data between sources
    """

    arg_dest = Arg(
        "dest", help="Sources merge records into", type=BaseSource.load_labeled
    )
    arg_src = Arg(
        "src",
        help="Sources to pull records from",
        type=BaseSource.load_labeled,
    )

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


class ImportExportCMD(PortCMD, SourcesCMD):
    """Shared import export arguments"""

    arg_filename = Arg("filename", type=str)


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
