# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import ast
import argparse

from ..data import parser_helper


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


class ParseInputsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]
        ouput_specs = [
            (
                parser_helper(value.split("=", maxsplit=1)[0]),
                value.split("=", maxsplit=1)[1],
            )
            for value in values
        ]
        setattr(namespace, self.dest, ouput_specs)
