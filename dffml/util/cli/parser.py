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
from ...source.source import BaseSource, Sources
from ...model import Model

from ...df.base import Operation, OperationImplementation

from .cmd import ParseLoggingAction


def list_action(list_class):
    """
    Action to take a list of values and make them values in the list of type
    list_class. Which will be a class descendent from AsyncContextManagerList.
    """

    class ParseExpandAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if not isinstance(values, list):
                values = [values]
            setattr(namespace, self.dest, list_class(*values))

    return ParseExpandAction


class ParseOutputSpecsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        ouput_specs = [
            (
                ast.literal_eval(value.split("=", maxsplit=1)[0]),
                value.split("=", maxsplit=1)[1],
            )
            for value in values
        ]
        setattr(namespace, self.dest, ouput_specs)


ParseInputsAction = ParseOutputSpecsAction


class ParseRemapAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        inputs = []
        for value in values:
            output_operation, sub = value.split(".", maxsplit=1)
            sub, feature = sub.split("=", maxsplit=1)
            inputs.append((output_operation, sub, feature))
        setattr(namespace, self.dest, inputs)
