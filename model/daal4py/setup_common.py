import os
import sys
import ast
from pathlib import Path
from setuptools import find_packages

ORG = "intel"
NAME = "dffml-model-daal4py"
DESCRIPTION = "DFFML model daal4py"
AUTHOR_NAME = "Ch.M.Hashim"
AUTHOR_EMAIL = "hashimchaudry23@gmail.com"
# Install dffml if it is not installed in development mode
INSTALL_REQUIRES = [
    # See https://github.com/intel/dffml/issues/766
    # "daal4py>=0.2020.0",
    "pandas>=0.25.0",
    "joblib>=0.13.2",
    "numpy>=1.16.4",
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

SELF_PATH = Path(sys.argv[0]).parent.resolve()
if not (SELF_PATH / Path(IMPORT_NAME, "version.py")).is_file():
    SELF_PATH = os.path.dirname(os.path.realpath(__file__))

VERSION = ast.literal_eval(
    Path(SELF_PATH, IMPORT_NAME, "version.py")
    .read_text()
    .split("=")[-1]
    .strip()
)

README = Path(SELF_PATH, "README.md").read_text()

KWARGS = dict(
    name="dffml-model-daal4py",
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    maintainer="John Andersen",
    maintainer_email="john.s.andersen@intel.com",
    url=f"https://github.com/{ORG}/{NAME}",
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
)
