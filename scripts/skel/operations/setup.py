import os
import ast
from io import open

from setuptools import find_packages, setup

self_path = os.path.dirname(os.path.realpath(__file__))

NAME = "dffml_operations_operations_name"
AUTHOR_NAME = "John Andersen"
AUTHOR_EMAIL = "john.s.andersen@intel.com"
DESCRIPTION = "Opeartions for a calculator"

with open(os.path.join(self_path, NAME, "version.py"), "r") as f:
    for line in f:
        if line.startswith("VERSION"):
            version = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(self_path, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

INSTALL_REQUIRES = []

setup(
    name=NAME,
    version=version,
    description=DESCRIPTION,
    long_description=readme,
    long_description_content_type="text/markdown",
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR_NAME,
    maintainer_email=AUTHOR_EMAIL,
    url="https://github.com/intel/dffml/blob/master/operations/operations_name/README.md",
    license="MIT",
    keywords=[""],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=INSTALL_REQUIRES,
    tests_require=[],
    packages=find_packages(),
    entry_points={
        "dffml.operation": [
            "calc_add = " + NAME + ".operations:calc_add.op",
            "calc_mult = " + NAME + ".operations:calc_mult.op",
            "calc_parse_line = " + NAME + ".operations:calc_parse_line.op",
        ],
        "dffml.operation.implementation": [
            "calc_add = " + NAME + ".operations:calc_add.imp",
            "calc_mult = " + NAME + ".operations:calc_mult.imp",
            "calc_parse_line = " + NAME + ".operations:calc_parse_line.imp",
        ],
    },
)
