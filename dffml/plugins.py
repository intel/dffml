"""
This file is imported by the top level setup.py and therefore must remain as
independent as possible (no relative imports)
"""
import os
import sys


def inpath(binary):
    return any(
        list(
            map(
                lambda dirname: os.path.isfile(os.path.join(dirname, binary)),
                os.environ.get("PATH", "").split(":"),
            )
        )
    )


# List of plugins
CORE_PLUGINS = [
    ("configloader", "yaml"),
    ("configloader", "image"),
    ("model", "scratch"),
    ("model", "scikit"),
    ("model", "tensorflow"),
    ("model", "tensorflow_hub"),
    ("model", "transformers"),
    ("model", "vowpalWabbit"),
    ("model", "autosklearn"),
]

# Models which currently don't support Python 3.8
if sys.version_info.major == 3 and sys.version_info.minor < 8:
    CORE_PLUGINS += [
        ("model", "daal4py"),
    ]

CORE_PLUGINS += [
    ("examples", "shouldi"),
    ("feature", "git"),
    ("feature", "auth"),
    ("operations", "binsec"),
    ("operations", "deploy"),
    ("operations", "image"),
    ("operations", "nlp"),
    ("service", "http"),
    ("source", "mysql"),
]

# Dependencies of plugins and how to check if they exist on the system or not
CORE_PLUGIN_DEPS = {
    ("model", "vowpalWabbit"): {"cmake": lambda: inpath("cmake")},
    ("model", "autosklearn"): {
        "swig": lambda: inpath("swig"),
        "cython": lambda: inpath("cython"),
    },
}

# All packages under configloader/ are really named dffml-config-{name}
ALTERNATIVES = {"configloader": "config"}

# Build a dict of plugin_type_name (aka model, config): list(package_names)
PACKAGE_NAMES_BY_PLUGIN = {
    (plugin_type + ("s" if not plugin_type.endswith("s") else "")): [
        "dffml-%s-%s"
        % (ALTERNATIVES.get(plugin_type, plugin_type), name.replace("_", "-"),)
        for sub_plugin_type, name in CORE_PLUGINS
        if sub_plugin_type == plugin_type
    ]
    for plugin_type, _ in CORE_PLUGINS
    if plugin_type != "examples"
}
# Operations used to be named featues
PACKAGE_NAMES_BY_PLUGIN["operations"].extend(
    PACKAGE_NAMES_BY_PLUGIN["features"]
)
del PACKAGE_NAMES_BY_PLUGIN["features"]

# All packages
PACKAGE_NAMES_BY_PLUGIN["all"] = [
    "dffml-%s-%s"
    % (ALTERNATIVES.get(plugin_type, plugin_type), name.replace("_", "-"),)
    for plugin_type, name in CORE_PLUGINS
    if plugin_type != "examples"
]
