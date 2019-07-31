from setuptools import setup

from dffml_setup_common import SETUP_KWARGS, IMPORT_NAME

SETUP_KWARGS["entry_points"] = {
    "dffml.operation": [
        f"calc_add = {IMPORT_NAME}.operations:calc_add.op",
        f"calc_mult = {IMPORT_NAME}.operations:calc_mult.op",
        f"calc_parse_line = {IMPORT_NAME}.operations:calc_parse_line.op",
    ],
    "dffml.operation.implementation": [
        f"calc_add = {IMPORT_NAME}.operations:calc_add.imp",
        f"calc_mult = {IMPORT_NAME}.operations:calc_mult.imp",
        f"calc_parse_line = {IMPORT_NAME}.operations:calc_parse_line.imp",
    ],
}

setup(**SETUP_KWARGS)
