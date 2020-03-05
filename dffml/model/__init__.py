# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
All models registered to the dffml.model entry point using setuptools are
derived from the Model class. To add a model, create a module which has a
setup.py which specifies where to find your Model subclass within your module.

>>> setup(
>>>     name='mymodel',
...
>>>     entry_points={
>>>         'dffml.model': [
>>>             'mymodel = mymodel:MyModel',
>>>         ],
>>>     },
>>> )
"""
from .model import Model, ModelContext, SimpleModel, ModelNotTrained
