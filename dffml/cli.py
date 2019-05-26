# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Command line interface evaluates packages given their source URLs
"""
import os
import sys
import pdb
import json
import asyncio
import logging
import inspect
import argparse
import pkg_resources

from .log import LOGGER
from .version import VERSION
from .repo import Repo
from .port import Port
from .feature import Feature, Features, Data
from .source.source import BaseSource, Sources, SubsetSources
from .model import Model
from .df.types import Input
from .df.base import StringInputSetContext
from .df.memory import MemoryInputSet, MemoryInputSetConfig
from .util.cli.arg import Arg
from .util.cli.cmd import CMD
from .util.cli.cmds import (
    SourcesCMD,
    FeaturesCMD,
    ModelCMD,
    PortCMD,
    KeysCMD,
    ListEntrypoint,
    OrchestratorCMD,
)


class Version(CMD):
    """
    Print version and exit
    """

    async def run(self):
        LOGGER.debug("Reporting version")
        print(VERSION)


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


class OperationsCMD(OrchestratorCMD, SourcesCMD):

    arg_sources = SourcesCMD.arg_sources.modify(required=False)
    arg_caching = Arg(
        "-caching",
        help="Re-run operations or use last",
        required=False,
        default=False,
        action="store_true",
    )
    arg_cacheless = Arg(
        "-cacheless",
        help="Do not re-run operations if these features are missing",
        required=False,
        default=[],
        nargs="+",
    )
    arg_update = Arg(
        "-update",
        help="Update repo with sources",
        required=False,
        default=False,
        action="store_true",
    )


class OperationsAll(OperationsCMD):
    """Operations all repos in sources"""

    async def repos(self, sctx):
        async for repo in sctx.repos():
            yield repo

    async def run_operations(self, dff, sources):
        # Orchestrate the running of these operations
        async with dff() as dffctx, sources() as sctx:
            # Create the inputs for the ouput operations
            output_specs = [
                Input(
                    value=value,
                    definition=self.definitions[def_name],
                    parents=False,
                )
                for value, def_name in self.output_specs
            ]

            # Add our inputs to the input network with the context being the
            # repo src_url
            async for repo in self.repos(sctx):
                inputs = []
                for value, def_name in self.inputs:
                    inputs.append(
                        Input(
                            value=value,
                            definition=self.definitions[def_name],
                            parents=False,
                        )
                    )
                if self.repo_def:
                    inputs.append(
                        Input(
                            value=repo.src_url,
                            definition=self.definitions[self.repo_def],
                            parents=False,
                        )
                    )

                await dffctx.ictx.add(
                    MemoryInputSet(
                        MemoryInputSetConfig(
                            ctx=StringInputSetContext(repo.src_url),
                            inputs=inputs + output_specs,
                        )
                    )
                )

            async for ctx, results in dffctx.run_operations(strict=True):
                ctx_str = (await ctx.handle()).as_string()
                # TODO Make a RepoInputSetContext which would let us store the
                # repo instead of recalling it by the URL
                repo = await sctx.repo(ctx_str)
                # Remap the output operations to their feature
                remap = {}
                for output_operation_name, sub, feature_name in self.remap:
                    if not output_operation_name in results:
                        self.logger.error(
                            "[%s] results do not contain %s: %s",
                            ctx_str,
                            output_operation_name,
                            results,
                        )
                        continue
                    if not sub in results[output_operation_name]:
                        self.logger.error(
                            "[%s] %r is not in: %s",
                            ctx_str,
                            sub,
                            results[output_operation_name],
                        )
                        continue
                    remap[feature_name] = results[output_operation_name][sub]
                # Store the results
                repo.evaluated(remap)
                yield repo
                if self.update:
                    await sctx.update(repo)

    async def run(self):
        async with self.dff as dff, self.sources as sources:
            async for repo in self.run_operations(dff, sources):
                yield repo


class OperationsRepo(OperationsAll, KeysCMD):
    """Operations features on individual repos"""

    async def repos(self, sctx):
        for src_url in self.keys:
            yield await sctx.repo(src_url)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = SubsetSources(*self.sources, keys=self.keys)


class Operations(CMD):
    """Run operations for repos"""

    repo = OperationsRepo
    _all = OperationsAll


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

    arg_classifications = Arg("-classifications", nargs="+", required=True)


class Train(MLCMD):
    """Train a model on data from given sources"""

    async def run(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model() as mctx:
                return await mctx.train(sctx, features, self.classifications)


class Accuracy(MLCMD):
    """Assess model accuracy on data from given sources"""

    async def run(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model() as mctx:
                return float(
                    await mctx.accuracy(sctx, features, self.classifications)
                )


class PredictAll(EvaluateAll, MLCMD):
    """Predicts for all sources"""

    async def predict(self, mctx, sctx, features, repos):
        async for repo, classification, confidence in mctx.predict(
            repos, features, self.classifications
        ):
            repo.predicted(classification, confidence)
            yield repo
            if self.update:
                await sctx.update(repo)

    async def run(self):
        async with self.sources as sources, self.features as features, self.model as model:
            async with sources() as sctx, model() as mctx:
                async for repo in self.predict(
                    mctx, sctx, features, sctx.repos()
                ):
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
    operations = Operations
    evaluate = Evaluate
    service = services()
    applicable = Applicable
