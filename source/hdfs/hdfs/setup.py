from setuptools import setup

from dffml_setup_common import SETUP_KWARGS, IMPORT_NAME

SETUP_KWARGS["install_requires"] += ["hdfscli>=2.5.8"]
SETUP_KWARGS["tests_require"] = ["docker>=4.0.2"]
SETUP_KWARGS["entry_points"] = {
    "dffml.source": [f"misc = {IMPORT_NAME}.source:HDFSSource"]
}

setup(**SETUP_KWARGS)