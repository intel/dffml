# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import copy
from typing import Optional

from ..data import traverse_config_set


def parse_unknown(*unknown):
    parsed = {}
    name = []
    add_to_parsed = []
    for arg in unknown:
        if arg.startswith("-"):
            if not name:
                name = arg.lstrip("-").split("-")
            if not add_to_parsed:
                traverse_config_set(parsed, *name, [True])
            else:
                traverse_config_set(parsed, *name, add_to_parsed)
            name = arg.lstrip("-").split("-")
            add_to_parsed = []
        else:
            add_to_parsed.append(arg)
    if unknown and name:
        if not add_to_parsed:
            traverse_config_set(parsed, *name, [True])
        else:
            traverse_config_set(parsed, *name, add_to_parsed)
    return parsed


class Arg(dict):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "no-name"
        if args:
            self.name = args[0]

    def modify(self, name: Optional[str] = None, **kwargs):
        updated = copy.deepcopy(self)
        updated.update(kwargs)
        if not name is None:
            updated.name = name
        return updated
