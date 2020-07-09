import os
import importlib.util
from setuptools import setup

# Boilerplate to load commonalities
spec = importlib.util.spec_from_file_location(
    "setup_common", os.path.join(os.path.dirname(__file__), "setup_common.py")
)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

common.KWARGS["install_requires"] += [
    "opencv-python>=4.2.0.34",
    "numpy>=1.16.2",
]
common.KWARGS["entry_points"] = {
    "dffml.configloader": [
        f"png = {common.IMPORT_NAME}.configloader:PNGConfigLoader",
        f"jpg = {common.IMPORT_NAME}.configloader:JPGConfigLoader",
        f"jpeg = {common.IMPORT_NAME}.configloader:JPEGConfigLoader",
        f"tiff = {common.IMPORT_NAME}.configloader:TIFFConfigLoader",
    ]
}

setup(**common.KWARGS)
