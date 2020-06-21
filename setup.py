# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import ast
import pathlib
from io import open
import importlib.util
from setuptools import find_packages, setup

with open(pathlib.Path("dffml", "version.py"), "r") as f:
    for line in f:
        if line.startswith("VERSION"):
            VERSION = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

# Load file by path
spec = importlib.util.spec_from_file_location(
    "plugins", os.path.join(os.path.dirname(__file__), "dffml", "plugins.py")
)
plugins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugins)

# All packages under configloader/ are really named dffml-config-{name}
ALTERNATIVES = {"configloader": "config"}
ALTERNATIVES_FEATURE_TO_OP = ALTERNATIVES.copy()
ALTERNATIVES_FEATURE_TO_OP.update({"feature": "operation"})
EXTRAS_REQUIRES = {
    (
        ALTERNATIVES_FEATURE_TO_OP.get(plugin_type, plugin_type)
        + ("s" if not plugin_type.endswith("s") else "")
    ): [
        "dffml-%s-%s"
        % (ALTERNATIVES.get(plugin_type, plugin_type), name.replace("_", "-"),)
        for sub_plugin_type, name in plugins.CORE_PLUGINS
        if sub_plugin_type == plugin_type
    ]
    for plugin_type, _ in plugins.CORE_PLUGINS
    if plugin_type != "examples"
}

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
        "all": [
            "dffml-%s-%s"
            % (
                ALTERNATIVES.get(plugin_type, plugin_type),
                name.replace("_", "-"),
            )
            for plugin_type, name in plugins.CORE_PLUGINS
        ],
        "dev": [
            "coverage",
            "codecov",
            "sphinx",
            "sphinx_rtd_theme",
            "recommonmark",
            "black",
            "jsbeautifier",
            "twine",
        ],
        **EXTRAS_REQUIRES,
    },
    tests_require=["httptest>=0.0.15", "Pillow>=7.1.2", "numpy>=1.16.2"],
    entry_points={
        "console_scripts": ["dffml = dffml.cli.cli:CLI.main"],
        "dffml.source": [
            "csv = dffml.source.csv:CSVSource",
            "json = dffml.source.json:JSONSource",
            "memory = dffml.source.memory:MemorySource",
            "idx1 = dffml.source.idx1:IDX1Source",
            "idx3 = dffml.source.idx3:IDX3Source",
            "db = dffml.source.db:DbSource",
            "ini = dffml.source.ini:INISource",
            "df = dffml.source.df:DataFlowSource",
            "op = dffml.source.op:OpSource",
            "dir = dffml.source.dir:DirectorySource",
        ],
        "dffml.port": ["json = dffml.port.json:JSON"],
        "dffml.service.cli": ["dev = dffml.service.dev:Develop"],
        "dffml.configloader": [
            "json = dffml.configloader.json:JSONConfigLoader"
        ],
        # Data Flow
        "dffml.operation": [
            # Output
            "group_by = dffml.operation.output:GroupBy",
            "get_single = dffml.operation.output:GetSingle",
            "get_multi = dffml.operation.output:GetMulti",
            "associate = dffml.operation.output:Associate",
            "associate_definition = dffml.operation.output:AssociateDefinition",
            # Mapping
            "dffml.mapping.extract = dffml.operation.mapping:mapping_extract_value",
            "dffml.mapping.create = dffml.operation.mapping:create_mapping",
            # Dataflow
            "dffml.dataflow.run = dffml.operation.dataflow:run_dataflow",
            # Model
            "dffml.model.predict = dffml.operation.model:model_predict",
            # io
            "AcceptUserInput = dffml.operation.io:AcceptUserInput",
            "print_output = dffml.operation.io:print_output",
            # preprocess
            "literal_eval = dffml.operation.preprocess:literal_eval",
            # math
            "multiply = dffml.operation.math:multiply",
            # Database
            "db_query_create_table = dffml.operation.db:db_query_create_table",
            "db_query_insert = dffml.operation.db:db_query_insert",
            "db_query_update = dffml.operation.db:db_query_update",
            "db_query_remove = dffml.operation.db:db_query_remove",
            "db_query_insert_or_update = dffml.operation.db:db_query_insert_or_update",
            "db_query_lookup = dffml.operation.db:db_query_lookup",
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
        # Databases
        "dffml.db": ["sqlite = dffml.db.sqlite:SqliteDatabase"],
        # Models
        "dffml.model": ["slr = dffml.model.slr:SLRModel"],
        # Secrets
        "dffml.secret": ["ini = dffml.secret.ini:INISecret"],
    },
)
