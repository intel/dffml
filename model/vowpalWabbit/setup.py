import os
import sys
import ast
from io import open
from setuptools import find_packages, setup

ORG = "intel"
NAME = "dffml-model-vowpalWabbit"
DESCRIPTION = "DFFML model vowpalWabbit"
AUTHOR_NAME = "Himanshu Tripathi"
AUTHOR_EMAIL = "himanshutripathi366@gmail.com"
INSTALL_REQUIRES = [
    "vowpalwabbit>=8.8.0",
    "scikit-learn>=0.21.2",
    "pandas>=0.25.0",
] + (
    ["dffml>=0.3.7"]
    if not any(
        list(
            map(
                os.path.isfile,
                list(
                    map(
                        lambda syspath: os.path.join(
                            syspath, "dffml.egg-link"
                        ),
                        sys.path,
                    )
                ),
            )
        )
    )
    else []
)

IMPORT_NAME = (
    NAME
    if "replace_package_name".upper() != NAME
    else "replace_import_package_name".upper()
).replace("-", "_")

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(SELF_PATH, IMPORT_NAME, "version.py"), "r") as f:
    for line in f:
        if line.startswith("VERSION"):
            version = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(SELF_PATH, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="dffml-model-vowpalWabbit",
    version=version,
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Himanshu Tripathi",
    author_email="himanshutripathi366@gmail.com",
    maintainer="John Andersen",
    maintainer_email="john.s.andersen@intel.com",
    url="https://github.com/intel/dffml/blob/master/model/vowpalWabbit/README.md",
    license="MIT",
    keywords=["dffml"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    entry_points={
        "dffml.model": [f"vwmodel = {IMPORT_NAME}.vw_base:VWModel",]
    },
)
