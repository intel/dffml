# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import ast
from io import open
from setuptools import find_packages, setup

with open("dffml/version.py", "r") as f:
    for line in f:
        if line.startswith("VERSION"):
            VERSION = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open("README.md", "r", encoding="utf-8") as f:
    README = f.read()

setup(
    name="dffml",
    version=VERSION,
    description="Data Flow Facilitator for Machine Learning",
    long_description=README,
    long_description_content_type="text/markdown",
    author="John Andersen",
    author_email="john.s.andersen@intel.com",
    maintainer="John Andersen",
    maintainer_email="john.s.andersen@intel.com",
    url="https://github.com/intel/dffml",
    license="MIT",
    keywords=[""],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        "models": [
            "dffml-model-tensorflow",
            "dffml-model-scratch",
            "dffml-model-scikit",
        ],
        "sources": ["dffml-source-mysql"],
        "dev": [
            "coverage",
            "codecov",
            "sphinx",
            "sphinxcontrib-asyncio",
            "black",
            "sphinx_rtd_theme",
        ],
    },
    entry_points={
        "console_scripts": ["dffml = dffml.cli.cli:CLI.main"],
        "dffml.source": [
            "csv = dffml.source.csv:CSVSource",
            "json = dffml.source.json:JSONSource",
            "memory = dffml.source.memory:MemorySource",
        ],
        "dffml.port": ["json = dffml.port.json:JSON"],
        "dffml.service.cli": ["dev = dffml.service.dev:Develop"],
        "dffml.config": ["json = dffml.config.json:JSONConfigLoader"],
        # Data Flow
        "dffml.operation": [
            # Output
            "group_by = dffml.operation.output:GroupBy",
            "get_single = dffml.operation.output:GetSingle",
            "associate = dffml.operation.output:Associate",
            # Mapping
            "dffml.mapping.extract = dffml.operation.mapping:mapping_extract_value",
            "dffml.mapping.create = dffml.operation.mapping:create_mapping",
        ],
        "dffml.kvstore": ["memory = dffml.df.memory:MemoryKeyValueStore"],
        "dffml.input.network": ["memory = dffml.df.memory:MemoryInputNetwork"],
        "dffml.operation.network": [
            "memory = dffml.df.memory:MemoryOperationNetwork"
        ],
        "dffml.redundancy.checker": [
            "memory = dffml.df.memory:MemoryRedundancyChecker"
        ],
        "dffml.lock.network": ["memory = dffml.df.memory:MemoryLockNetwork"],
        "dffml.operation.implementation.network": [
            "memory = dffml.df.memory:MemoryOperationImplementationNetwork"
        ],
        "dffml.orchestrator": ["memory = dffml.df.memory:MemoryOrchestrator"],
    },
)
