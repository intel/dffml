# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Education (dffml) is a package and tool for doing machine learning.

It uses the setuptools dynamic discovery of services and plugins [1] to
evaluate a package based on the installed features.

[1]: http://setuptools.readthedocs.io/en/latest/setuptools.html
"""
from .feature import Feature

# Used to declare our namespace for resource discovery
__import__("pkg_resources").declare_namespace(__name__)
