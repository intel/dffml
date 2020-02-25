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
    "dffml.db": [f"abstractdb = {common.IMPORT_NAME}.db:AbstractDatabase"],
    "dffml.source": [
        f"dbsource = {common.IMPORT_NAME}.source:DBAbstractionSource"
    ],
}

common.KWARGS["install_requires"] += ["aiomysql>=0.0.20"]

common.KWARGS["tests_require"] = ["docker>=4.0.2"]

setup(**common.KWARGS)
