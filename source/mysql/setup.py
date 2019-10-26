from setuptools import setup

from dffml_setup_common import SETUP_KWARGS, IMPORT_NAME

SETUP_KWARGS["install_requires"] += ["aiomysql>=0.0.20"]
SETUP_KWARGS["tests_require"] = ["docker>=4.0.2"]
SETUP_KWARGS["entry_points"] = {
    "dffml.source": [f"mysql = {IMPORT_NAME}.source:MySQLSource"]
}

setup(**SETUP_KWARGS)
