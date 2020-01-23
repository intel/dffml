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
    "dffml.db": [f"mysql = {common.IMPORT_NAME}.db:MySQLDatabase"],
    "dffml.source": [f"mysql = {common.IMPORT_NAME}.source:MySQLSource"],
}

common.KWARGS["install_requires"] += ["aiomysql>=0.0.20"]

common.KWARGS["tests_require"] = ["docker>=4.0.2"]

setup(**common.KWARGS)
