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

from ...df.base import Operation, \
                       OperationImplementation

from .base import ParseLoggingAction

from .log import LOGGER

LOGGER = LOGGER.getChild('cmds')

class ParseSourcesAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        parse = dict(map(lambda source: source.split('=', maxsplit=2)[::-1],
            values))
        values = Sources(*list(Source.load_from_dict(parse).values()))
        setattr(namespace, self.dest, values)

class ParseFeaturesAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, Features.load(*values))

class ParseOperationAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        setattr(namespace, self.dest, Operation.load_multiple(values).values())

class ParseOperationImplementationAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        setattr(namespace, self.dest,
                OperationImplementation.load_multiple(values).values())

class ParseInputNetworkAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, BaseInputNetwork.load(value))

class ParseOperationNetworkAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, BaseOperationNetwork.load(value))

class ParseLockNetworkAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, BaseLockNetwork.load(value))

class ParseRedundancyCheckerAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, BaseRedundancyChecker.load(value))

class ParseKeyValueStoreAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, BaseKeyValueStore.load(value))

class ParseOperationImplementationNetworkAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest,
                BaseOperationImplementationNetwork.load(value))

class ParseOrchestratorAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, BaseOrchestrator.load(value))

class ParseOutputSpecsAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        ouput_specs = [(ast.literal_eval(value.split('=', maxsplit=2)[0]),
                        value.split('=', maxsplit=2)[1],) \
                       for value in values]
        setattr(namespace, self.dest, ouput_specs)

ParseInputsAction = ParseOutputSpecsAction

class ParseRemapAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        inputs = []
        for value in values:
            output_operation, sub = value.split('.', maxsplit=2)
            sub, feature = sub.split('=', maxsplit=2)
            inputs.append((output_operation, sub, feature,))
        setattr(namespace, self.dest, inputs)

class ParseModelAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, Model.load(value)())

class ParsePortAction(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, Port.load(value)())
