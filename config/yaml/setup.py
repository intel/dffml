import os
import importlib.util
from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["install_requires"] += ["PyYAML>=5.1.2"]
common.KWARGS["entry_points"] = {
    "dffml.config": [f"yaml = {common.IMPORT_NAME}.config:YamlConfigLoader"]
}

setup(**common.KWARGS)
