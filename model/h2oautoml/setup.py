import importlib.util
import os

from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["entry_points"] = {
    "dffml.model": [
        f"h2oautoml = {common.IMPORT_NAME}.h2oautoml:H2oAutoMLModel"
    ]
}

setup(**common.KWARGS)
