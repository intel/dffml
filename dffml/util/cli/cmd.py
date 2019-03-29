# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import sys
import ast
import copy
import json
import asyncio
import inspect
import logging
import argparse
from typing import Optional

from ...repo import Repo
from ...port import Port
from ...feature import Feature, Features
from ...source import Source, Sources, JSONSource
from ...model import Model

from ...df.linker import Linker
from ...df.base import Input, \
                  BaseInputNetwork, \
                  BaseOperationNetwork, \
                  BaseLockNetwork, \
                  BaseRedundancyChecker, \
                  BaseOperationImplementationNetwork, \
                  BaseOrchestrator, \
                  StringInputSetContext

from ...df.memory import MemoryInputNetwork, \
                  MemoryOperationNetwork, \
                  MemoryLockNetwork, \
                  MemoryRedundancyChecker, \
                  MemoryOperationImplementationNetwork, \
                  MemoryOrchestrator, \
                  MemoryInputSet, \
                  MemoryInputSetConfig

from ...df.dff import DataFlowFacilitator

from .base import CMD, Arg

from .parser import ParseFeaturesAction, \
                    ParseSourcesAction, \
                    ParseModelAction, \
                    ParsePortAction, \
                    ParseOperationAction, \
                    ParseOperationImplementationAction, \
                    ParseInputNetworkAction, \
                    ParseOperationNetworkAction, \
                    ParseLockNetworkAction, \
                    ParseRedundancyCheckerAction, \
                    ParseOperationImplementationNetworkAction, \
                    ParseOrchestratorAction, \
                    ParseOutputSpecsAction, \
                    ParseInputsAction, \
                    ParseRemapAction

from .log import LOGGER

LOGGER = LOGGER.getChild('cmd')

class ListEntrypoint(CMD):
    '''
    Subclass this with an Entrypoint to display all registered classes.
    '''

    def display(self, cls):
        '''
        Print out the loaded but uninstantiated class
        '''
        if not cls.__doc__ is None:
            print('%s:' % (cls.__qualname__))
            print(cls.__doc__.rstrip())
        else:
            print('%s' % (cls.__qualname__))
        print()

    async def run(self):
        '''
        Display all classes registered with the entrypoint
        '''
        for cls in self.ENTRYPOINT.load():
            self.display(cls)

class FeaturesCMD(CMD):
    '''
    Set timeout for features
    '''

    arg_features = Arg('-features', nargs='+', required=True,
            default=Features(), action=ParseFeaturesAction)
    arg_timeout = Arg('-timeout', help='Feature evaluation timeout',
            required=False, default=Features.TIMEOUT, type=int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.features.timeout = self.timeout

class SourcesCMD(CMD):

    arg_sources = Arg('-sources', help='Sources for loading and saving',
            nargs='+', default=Sources(JSONSource(os.path.join(
                os.path.expanduser('~'), '.cache', 'dffml.json'))),
            action=ParseSourcesAction)

class ModelCMD(CMD):
    '''
    Set a models model dir.
    '''

    arg_model = Arg('-model', help='Model used for ML',
            action=ParseModelAction, required=True)
    arg_model_dir = Arg('-model_dir', help='Model directory for ML',
            default=os.path.join(os.path.expanduser('~'), '.cache', 'dffml'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model.model_dir = self.model_dir

class PortCMD(CMD):

    arg_port = Arg('port', action=ParsePortAction)

class KeysCMD(CMD):

    arg_keys = Arg('-keys', help='Key used for source lookup and evaluation',
            nargs='+', required=True)

class BaseDataFlowFacilitatorCMD(CMD):
    '''
    Set timeout for features
    '''

    arg_ops = Arg('-ops', required=True, nargs='+',
            action=ParseOperationAction)
    arg_input_network = Arg('-input-network',
            action=ParseInputNetworkAction, default=MemoryInputNetwork)
    arg_operation_network = Arg('-operation-network',
            action=ParseOperationNetworkAction, default=MemoryOperationNetwork)
    arg_lock_network = Arg('-lock-network',
            action=ParseLockNetworkAction, default=MemoryLockNetwork)
    arg_rchecker = Arg('-rchecker',
            action=ParseRedundancyCheckerAction,
            default=MemoryRedundancyChecker)
    # TODO We should be able to specify multiple operation implementation
    # networks. This would enable operations to live in different place,
    # accessed via the orchestrator transparently.
    arg_opimpn = Arg('-opimpn',
            action=ParseOperationImplementationNetworkAction,
            default=MemoryOperationImplementationNetwork)
    arg_orchestrator = Arg('-orchestrator',
            action=ParseOrchestratorAction, default=MemoryOrchestrator)
    arg_output_specs = Arg('-output-specs', required=True, nargs='+',
            action=ParseOutputSpecsAction)
    arg_inputs = Arg('-inputs', nargs='+',
            action=ParseInputsAction, default=[],
            help='Other inputs to add under each ctx (repo\'s src_url will ' + \
                 'be used as the context)')
    arg_repo_def = Arg('-repo-def', default=False, type=str,
            help='Definition to be used for repo.src_url.' + \
                 'If set, repo.src_url will be added to the set of inputs ' + \
                 'under each context (which is also the repo\'s src_url)')
    arg_remap = Arg('-remap', nargs='+', required=True,
            action=ParseRemapAction,
            help='For each repo, -remap output_operation_name.sub=feature_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dff = DataFlowFacilitator()
        self.linker = Linker()
        self.exported = self.linker.export(*self.ops)
        self.definitions, self.operations, _outputs = \
                self.linker.resolve(self.exported)

    # Load all entrypoints which may possibly be selected. Then have them add
    # their arguments to the DataFlowFacilitator-tots command.
    @classmethod
    def add_bases(cls):
        class LoadedDataFlowFacilitator(cls):
            pass
        for base in [BaseInputNetwork,
                     BaseOperationNetwork,
                     BaseLockNetwork,
                     BaseRedundancyChecker,
                     BaseOperationImplementationNetwork,
                     BaseOrchestrator]:
            for loaded in base.load():
                for arg_name, arg in loaded.args().items():
                    setattr(LoadedDataFlowFacilitator, arg_name, arg)
        return LoadedDataFlowFacilitator

DataFlowFacilitatorCMD = BaseDataFlowFacilitatorCMD.add_bases()
