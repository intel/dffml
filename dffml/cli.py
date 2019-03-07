# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Command line interface evaluates packages given their source URLs
'''
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
from .port import Port
from .feature import Feature, Features, Data
from .source import Source, Sources, SubsetSources
from .model import Model
from .util.cli import CMD, Arg, SourcesCMD, FeaturesCMD, ModelCMD, PortCMD, \
        KeysCMD, ListEntrypoint, ParseSourcesAction

class Version(CMD):
    '''
    Print version and exit
    '''

    async def run(self):
        LOGGER.debug('Reporting version')
        print(VERSION)

class Edit(SourcesCMD, KeysCMD):
    '''
    Edit each specified repo
    '''

    async def run(self):
        async with self.sources as sources:
            for key in self.keys:
                repo = await sources.repo(key)
                pdb.set_trace()
                await sources.update(repo)

class ListRepos(SourcesCMD):
    '''
    List repos stored in sources
    '''

    async def run(self):
        async with self.sources as sources:
            async for repo in sources.repos():
                print(repo)

class ListFeatures(ListEntrypoint):
    '''
    List installed features
    '''

    ENTRYPOINT = Feature

    def display(self, cls):
        if not cls.__doc__ is None:
            print('%s(%s):' % (cls.NAME, cls.__qualname__))
            print(cls.__doc__.rstrip())
        else:
            print('%s(%s)' % (cls.NAME, cls.__qualname__))
        print()

class ListServices(ListEntrypoint):
    '''
    List installed services
    '''

    async def run(self):
        for i in pkg_resources.iter_entry_points('dffml.service.cli'):
            loaded = i.load()
            if issubclass(loaded, CMD):
                self.display(loaded)

class ListSources(ListEntrypoint):
    '''
    List installed sources
    '''

    ENTRYPOINT = Source

class ListModels(ListEntrypoint):
    '''
    List installed models
    '''

    ENTRYPOINT = Model

class ListPorts(ListEntrypoint):
    '''
    List installed ports
    '''

    ENTRYPOINT = Port

class List(CMD):
    '''
    List repos and installed interfaces
    '''

    repos = ListRepos
    features = ListFeatures
    sources = ListSources
    models = ListModels
    services = ListServices
    ports = ListPorts

class Applicable(FeaturesCMD):

    arg_key = Arg('-key', help='Check if features is applicable for this key',
            required=True)

    async def run(self):
        async with self.features as features:
            return await features.applicable(Data(self.key))

class Merge(CMD):
    '''
    Merge repo data between sources
    '''

    arg_dest = Arg(name='dest', help='Sources merge repos into',
            action=ParseSourcesAction)
    arg_src = Arg('src', help='Sources to pull repos from',
            action=ParseSourcesAction)

    async def run(self):
        async with self.src, self.dest:
            async for repo in self.src.repos():
                repo.merge(await self.dest.repo(repo.src_url))
                await self.dest.update(repo)

class EvaluateCMD(FeaturesCMD, SourcesCMD):

    arg_sources = SourcesCMD.arg_sources.modify(required=False)
    arg_caching = Arg('-caching', help='Re-evaluate or use last',
            required=False, default=False, action='store_true')
    arg_parallel = Arg('-parallel', help='Evaluate in parallel',
            required=False, default=1, type=int)
    arg_cacheless = Arg('-cacheless',
            help='Do not re-evaluate if these features are missing',
            required=False, default=[], nargs='+')

class EvaluateAll(EvaluateCMD):
    '''Evaluate all repos in sources'''

    arg_update = Arg('-update', help='Update repo with sources', required=False,
            default=False, action='store_true')

    async def evaluate(self, sources, features):
        async for repo in features.evaluate_repos(sources.repos(),
                features=[name for name in features.names() \
                        if not name in self.cacheless],
                num_workers=self.parallel, caching=self.caching):
            yield repo
            if self.update:
                await sources.update(repo)

    async def run(self):
        async with self.sources as sources, self.features as features:
            async for repo in self.evaluate(sources, features):
                yield repo

class EvaluateRepo(EvaluateAll, KeysCMD):
    '''Evaluate features on individual repos'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = SubsetSources(*self.sources, keys=self.keys)

class Evaluate(CMD):
    '''Evaluate features against repos'''

    repo = EvaluateRepo
    _all = EvaluateAll

class MLCMD(ModelCMD, FeaturesCMD, SourcesCMD):
    '''
    Commands which use models share many similar arguments.
    '''

    arg_classifications = Arg('-classifications', nargs='+', required=True,
            default=[])

class Train(MLCMD):
    '''Train a model on data from given sources'''

    arg_steps = Arg('-steps', help='Number of steps', required=True, type=int,
            default=5000)
    arg_num_epochs = Arg('-num_epochs', help='Number of epochs', required=True,
            type=int, default=30)

    async def run(self):
        if not self.model_dir is None and not os.path.isdir(self.model_dir):
            os.makedirs(self.model_dir)
        async with self.sources as sources, self.features as features:
            return await self.model.train(sources, features,
                    self.classifications, self.steps, self.num_epochs)

class Accuracy(MLCMD):
    '''Assess model accuracy on data from given sources'''

    async def run(self):
        async with self.sources as sources, self.features as features:
            return float(await self.model.accuracy(sources, features,
                self.classifications))

class PredictAll(EvaluateAll, MLCMD):
    '''Predicts for all sources'''

    async def predict(self, sources, features, repos):
        async for repo, classification, confidence in \
                self.model.predict(repos, features, self.classifications):
            repo.predicted(classification, confidence)
            yield repo
            if self.update:
                await sources.update(repo)

    async def run(self):
        async with self.sources as sources, self.features as features:
            async for repo in self.predict(sources, features,
                    self.evaluate(sources, features)):
                yield repo

class PredictRepo(PredictAll, EvaluateRepo):
    '''Predictions for individual repos'''
    pass

class Predict(CMD):
    '''Evaluate features against repos and produce a prediction'''

    repo = PredictRepo
    _all = PredictAll

class ImportExportCMD(PortCMD, SourcesCMD):
    '''Shared import export arguments'''

    arg_filename = Arg('filename', type=str)

class Import(ImportExportCMD):
    '''Imports repos'''

    async def run(self):
        async with self.sources as sources:
            return await self.port.import_from_file(sources, self.filename)

class Export(ImportExportCMD):
    '''Exports repos'''

    async def run(self):
        async with self.sources as sources:
            return await self.port.export_to_file(sources, self.filename)

def services():
    '''
    Loads dffml.services.cli entrypoint and creates a CMD class incorporating
    all of the loaded CLI versions of services as subcommands.
    '''
    class Service(CMD):
        '''
        Expose various functionalities of dffml
        '''
        pass
    for i in pkg_resources.iter_entry_points('dffml.service.cli'):
        loaded = i.load()
        if issubclass(loaded, CMD):
            setattr(Service, i.name, loaded)
    return Service

class CLI(CMD):
    '''
    CLI interface for dffml
    '''

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
