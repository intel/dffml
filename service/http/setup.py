import os
import sys
import ast
from io import open
from setuptools import find_packages, setup

ORG = "intel"
NAME = "dffml-service-http"
DESCRIPTION = "DFFML HTTP API Service"
AUTHOR_NAME = "John Andersen"
AUTHOR_EMAIL = "john.s.andersen@intel.com"
# Install dffml if it is not installed in development mode
INSTALL_REQUIRES = ["aiohttp>=3.5.4", "aiohttp_cors>=0.7.0"] + (
    ["dffml>=0.3.0"]
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
            VERSION = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(SELF_PATH, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=readme,
    long_description_content_type="text/markdown",
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR_NAME,
    maintainer_email=AUTHOR_EMAIL,
    url=f"https://github.com/{ORG}/dffml/tree/master/service/http",
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
        "dffml.service.cli": [f"http = {IMPORT_NAME}.cli:HTTPService"]
    },
)
