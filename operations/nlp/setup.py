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
        f"remove_stopwords = {common.IMPORT_NAME}.operations:remove_stopwords",
        f"get_embedding = {common.IMPORT_NAME}.operations:get_embedding",
    ]
}

setup(**common.KWARGS)
