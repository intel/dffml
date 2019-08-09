from setuptools import setup

from dffml_setup_common import SETUP_KWARGS, IMPORT_NAME

SETUP_KWARGS["tests_require"] = [
    "docker>=4.0.2"
    ]
SETUP_KWARGS["entry_points"] = {
    "dffml.service.cli": [f"misc = {IMPORT_NAME}.misc:Misc"]
}

setup(**SETUP_KWARGS)
