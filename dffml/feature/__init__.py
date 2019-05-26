# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
All features registered to the dffml.feature entry point using setuptools are
derived from the Feature class. To add a feature, create a module which has a
setup.py which specifies where to find your Feature subclass within your module.

>>> setup(
>>>     name='myfeatures',
...
>>>     entry_points={
>>>         'dffml.feature': [
>>>             'numfiles = myfeatures:NumFilesFeature',
>>>         ],
>>>     },
>>> )
"""
from .feature import Data, Feature, Features, LoggingDict, DefFeature

# Declares dffml.feature is a namespace package
__import__("pkg_resources").declare_namespace(__name__)
