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
        f"get_payload = {common.IMPORT_NAME}.operations:get_payload",
        f"get_url_from_payload = {common.IMPORT_NAME}.operations:get_url_from_payload",
    ]
}

setup(**common.KWARGS)
