# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Command line interface evaluates packages given their source URLs
"""
import os
import sys
import pdb
import json
import pathlib
import asyncio
import logging
import inspect
import argparse
import contextlib
import pkg_resources
from typing import List

from ..version import VERSION
from ..base import BaseConfig
from ..repo import Repo
from ..port import Port
from ..feature import Feature, Features, Data
from ..source.source import BaseSource, Sources, SubsetSources
from ..model import Model
from ..config.config import BaseConfigLoader
from ..config.json import JSONConfigLoader
from ..df.types import Input, Operation, DataFlow
from ..df.base import StringInputSetContext
from ..df.memory import MemoryInputSet, MemoryInputSetConfig
from ..util.entrypoint import load
from ..util.data import merge
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..util.cli.cmds import (
    SourcesCMD,
    FeaturesCMD,
    ModelCMD,
    PortCMD,
    KeysCMD,
    ListEntrypoint,
)

from .dataflow import Dataflow
from .config import Config


class Version(CMD):
    """
    Print version and installed dffml packages
    """

    async def run(self):
        self.logger.debug("Reporting version")
        devmode = False
        for syspath in map(pathlib.Path, sys.path):
            if (syspath / "dffml.egg-link").is_file():
                devmode = True
        print(f"dffml version {VERSION} (devmode: {str(devmode).lower()})")


class Edit(SourcesCMD, KeysCMD):
    """
    Edit each specified repo
    """

    async def run(self):
        async with self.sources as sources:
            async with sources() as sctx:
                for key in self.keys:
                    repo = await sctx.repo(key)
                    pdb.set_trace()
                    await sctx.update(repo)


class ListRepos(SourcesCMD):
    """
    List repos stored in sources
    """

    async def run(self):
        async with self.sources as sources:
            async with sources() as sctx:
                async for repo in sctx.repos():
                    print(repo)


class ListFeatures(ListEntrypoint):
    """
    List installed features
    """

    ENTRYPOINT = Feature

    def display(self, cls):
        if not cls.__doc__ is None:
            print("%s(%s):" % (cls.NAME, cls.__qualname__))
            print(cls.__doc__.rstrip())
        else:
            print("%s(%s)" % (cls.NAME, cls.__qualname__))
        print()


class ListServices(ListEntrypoint):
    """
    List installed services
    """

    async def run(self):
        for i in pkg_resources.iter_entry_points("dffml.service.cli"):
            loaded = i.load()
            if issubclass(loaded, CMD):
                self.display(loaded)


class ListSources(ListEntrypoint):
    """
    List installed sources
    """

    ENTRYPOINT = BaseSource


class ListModels(ListEntrypoint):
    """
    List installed models
    """

    ENTRYPOINT = Model


class ListPorts(ListEntrypoint):
    """
    List installed ports
    """

    ENTRYPOINT = Port


class List(CMD):
    """
    List repos and installed interfaces
    """

    repos = ListRepos
    features = ListFeatures
    sources = ListSources
    models = ListModels
    services = ListServices
    ports = ListPorts


class Applicable(FeaturesCMD):

    arg_key = Arg(
        "-key",
        help="Check if features is applicable for this key",
        required=True,
    )

    async def run(self):
        async with self.features as features:
            return await features.applicable(Data(self.key))


class Merge(CMD):
    """
    Merge repo data between sources
    """

    arg_dest = Arg(
        "dest", help="Sources merge repos into", type=BaseSource.load_labeled
    )
    arg_src = Arg(
        "src", help="Sources to pull repos from", type=BaseSource.load_labeled
    )

    async def run(self):
        async with self.src.withconfig(
            self.extra_config
        ) as src, self.dest.withconfig(self.extra_config) as dest:
            async with src() as sctx, dest() as dctx:
                async for src in sctx.repos():
                    repo = Repo(src.src_url)
                    repo.merge(src)
                    repo.merge(await dctx.repo(repo.src_url))
                    await dctx.update(repo)


class EvaluateCMD(FeaturesCMD, SourcesCMD):

    arg_sources = SourcesCMD.arg_sources.modify(required=False)
    arg_caching = Arg(
        "-caching",
        help="Re-evaluate or use last",
        required=False,
        default=False,
        action="store_true",
    )
    arg_parallel = Arg(
        "-parallel",
        help="Evaluate in parallel",
        required=False,
        default=1,
        type=int,
    )
    arg_cacheless = Arg(
        "-cacheless",
        help="Do not re-evaluate if these features are missing",
        required=False,
        default=[],
        nargs="+",
    )


class EvaluateAll(EvaluateCMD):
    """Evaluate all repos in sources"""

    arg_update = Arg(
        "-update",
        help="Update repo with sources",
        required=False,
        default=False,
        action="store_true",
    )

    async def evaluate(self, sources, features):
        async with sources() as sctx:
            async for repo in features.evaluate_repos(
                sctx.repos(),
                features=[
                    name
                    for name in features.names()
                    if not name in self.cacheless
                ],
                num_workers=self.parallel,
                caching=self.caching,
            ):
                yield repo
                if self.update:
                    await sctx.update(repo)

    async def run(self):
        async with self.sources as sources, self.features as features:
            async for repo in self.evaluate(sources, features):
                yield repo


class EvaluateRepo(EvaluateAll, KeysCMD):
    """Evaluate features on individual repos"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = SubsetSources(*self.sources, keys=self.keys)


class Evaluate(CMD):
    """Evaluate features against repos"""

    repo = EvaluateRepo
    _all = EvaluateAll


class MLCMD(ModelCMD, FeaturesCMD, SourcesCMD):
    """
    Commands which use models share many similar arguments.
    """


class Train(MLCMD):
    """Train a model on data from given sources"""

    async def run(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                return await mctx.train(sctx)


class Accuracy(MLCMD):
    """Assess model accuracy on data from given sources"""

    async def run(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                return float(await mctx.accuracy(sctx))


class PredictAll(EvaluateAll, MLCMD):
    """Predicts for all sources"""

    async def predict(self, mctx, sctx, repos):
        async for repo in mctx.predict(repos):
            yield repo
            if self.update:
                await sctx.update(repo)

    async def run(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model(features) as mctx:
                async for repo in self.predict(mctx, sctx, sctx.repos()):
                    yield repo


class PredictRepo(PredictAll, EvaluateRepo):
    """Predictions for individual repos"""


class Predict(CMD):
    """Evaluate features against repos and produce a prediction"""

    repo = PredictRepo
    _all = PredictAll


class ImportExportCMD(PortCMD, SourcesCMD):
    """Shared import export arguments"""

    arg_filename = Arg("filename", type=str)


class Import(ImportExportCMD):
    """Imports repos"""

    async def run(self):
        async with self.sources as sources:
            async with sources() as sctx:
                return await self.port.import_from_file(sctx, self.filename)


class Export(ImportExportCMD):
    """Exports repos"""

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
    evaluate = Evaluate
    service = services()
    applicable = Applicable
    dataflow = Dataflow
    config = Config
