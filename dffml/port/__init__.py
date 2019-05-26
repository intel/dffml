# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
All ports registered to the dffml.port entry point using setuptools are
derived from the Port class. To add a port, create a module which has a
setup.py which specifies where to find your Port subclass within your module.

>>> setup(
>>>     name='myport',
...
>>>     entry_points={
>>>         'dffml.port': [
>>>             'myport = myport:MyPort',
>>>         ],
>>>     },
>>> )
"""
from .port import Port

# Declares dffml.port as a namespace package
__import__("pkg_resources").declare_namespace(__name__)
