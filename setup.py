# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import ast
from io import open
from setuptools import find_packages, setup

with open('dffml/version.py', 'r') as f:
    for line in f:
        if line.startswith('VERSION'):
            version = ast.literal_eval(line.strip().split('=')[-1].strip())
            break

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='dffml',
    version=version,
    description='Data Flow Facilitator for Machine Learning',
    long_description=readme,
    author='John Andersen',
    author_email='john.s.andersen@intel.com',
    maintainer='John Andersen',
    maintainer_email='john.s.andersen@intel.com',
    url='https://github.com/intel/dffml',
    license='MIT',
    keywords=[
        '',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    packages=find_packages(),
    extras_require={
        'tensorflow': ['dffml-model-tensorflow'],
        'git': ['dffml-feature-git'],
    },
    entry_points={
        'console_scripts': [
            'dffml = dffml.cli:CLI.main',
        ],
        'dffml.source': [
            'csv = dffml.source.csvfile:CSVSource',
            'json = dffml.source.json:JSONSource',
            'memory = dffml.source.memory:MemorySource',
        ],
        'dffml.port': [
            'json = dffml.port.json:JSON',
        ],
    },
)
