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
        f"calc_add = {common.IMPORT_NAME}.operations:calc_add",
        f"calc_mult = {common.IMPORT_NAME}.operations:calc_mult",
        f"calc_parse_line = {common.IMPORT_NAME}.operations:calc_parse_line",
    ]
}

setup(**common.KWARGS)
