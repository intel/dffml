import os
import importlib.util
from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["install_requires"] += ["xgboost>=1.1.1"]
common.KWARGS["install_requires"] += ["joblib>=0.16.0"]
common.KWARGS["entry_points"] = {
    "dffml.model": [
        f"xdgregressor = {common.IMPORT_NAME}.xdgregressor:XDGRegressorModel"
    ]
}

setup(**common.KWARGS)
