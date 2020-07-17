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
    ("model", "pytorch"),
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

# Plugins which currently don't support Python 3.8
if sys.version_info.major == 3 and sys.version_info.minor < 8:
    CORE_PLUGINS += [
        ("model", "daal4py"),
    ]

# Dependencies of plugins and how to check if they exist on the system or not
CORE_PLUGIN_DEPS = {
    ("model", "vowpalWabbit"): {"cmake": lambda: inpath("cmake")},
    ("model", "autosklearn"): {
        "swig": lambda: inpath("swig"),
        "cython": lambda: inpath("cython"),
    },
}
