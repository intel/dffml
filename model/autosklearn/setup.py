import os
import importlib.util
from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["install_requires"] += ["auto-sklearn>=0.7.0"]
common.KWARGS["entry_points"] = {
    "dffml.model": [
        "autoclassifier = dffml_model_autosklearn.autoclassifier:AutoSklearnClassifierModel",
    ]
}

setup(**common.KWARGS)
