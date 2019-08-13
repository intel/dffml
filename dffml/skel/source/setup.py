from setuptools import setup

from dffml_setup_common import SETUP_KWARGS, IMPORT_NAME

SETUP_KWARGS["entry_points"] = {
    "dffml.source": [f"misc = {IMPORT_NAME}.misc:Misc"]
}

setup(**SETUP_KWARGS)
