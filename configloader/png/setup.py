import os
import importlib.util
from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["install_requires"] += ["Pillow>=7.0.0", "numpy>=1.16.2"]
common.KWARGS["entry_points"] = {
    "dffml.configloader": [
        f"mnistpng = {common.IMPORT_NAME}.configloader:PNGConfigLoader"
    ]
}

setup(**common.KWARGS)
