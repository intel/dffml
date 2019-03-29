# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
'''
Declarative Directed Graph Execution
'''
from .types import *
from .linker import *
from .exceptions import *
from .base import *
from .dff import *
from .memory import *

# Declares dffml.ddge as a namespace package
__import__('pkg_resources').declare_namespace(__name__)
