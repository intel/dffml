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
    "dffml.operation": [
        f"resize = {common.IMPORT_NAME}.operations:resize",
        f"flatten = {common.IMPORT_NAME}.operations:flatten",
        f"calcHist = {common.IMPORT_NAME}.operations:calcHist",
        f"HuMoments = {common.IMPORT_NAME}.operations:HuMoments",
        f"Haralick = {common.IMPORT_NAME}.operations:Haralick",
        f"normalize = {common.IMPORT_NAME}.operations:normalize",
        f"convert_color = {common.IMPORT_NAME}.operations:convert_color",
    ]
}

setup(**common.KWARGS)
