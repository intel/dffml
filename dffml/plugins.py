import sys

CORE_PLUGINS = [
    ("configloader", "yaml"),
    ("configloader", "png"),
    ("model", "scratch"),
    ("model", "scikit"),
    ("model", "tensorflow"),
    ("model", "tensorflow_hub"),
    ("model", "transformers"),
    ("model", "vowpalWabbit"),
    ("model", "autosklearn"),
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
