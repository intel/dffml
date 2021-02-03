import os
import importlib.util
from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["entry_points"] = {
    "dffml.model": [
        f"xgbregressor = {common.IMPORT_NAME}.xgbregressor:XGBRegressorModel",
        f"xgbclassifier = {common.IMPORT_NAME}.xgbclassifier:XGBClassifierModel",
    ]
}

setup(**common.KWARGS)
