# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
All sources registered to the dffml.source entry point using setuptools are
derived from the Source class. To add a source, create a module which has a
setup.py which specifies where to find your Source subclass within your module.

>>> setup(
>>>     name='mysource',
...
>>>     entry_points={
>>>         'dffml.source': [
>>>             'mysource = mysource:MySource',
>>>         ],
>>>     },
>>> )
"""
# Declares dffml.source as a namespace package
__import__("pkg_resources").declare_namespace(__name__)
