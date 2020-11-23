import os
import sys
import ast
from pathlib import Path
from io import open

from setuptools import find_packages, setup

self_path = os.path.dirname(os.path.realpath(__file__))

with open(
    os.path.join(self_path, "dffml_model_tensorflow", "version.py"), "r"
) as f:
    for line in f:
        if line.startswith("VERSION"):
            version = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(self_path, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

# See https://github.com/intel/dffml/issues/816
INSTALL_REQUIRES = [] + (
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

REQUIREMENTS_TXT_PATH = Path(self_path, "requirements.txt")
if REQUIREMENTS_TXT_PATH.is_file():
    INSTALL_REQUIRES += list(
        map(lambda i: i.strip(), REQUIREMENTS_TXT_PATH.read_text().split("\n"))
    )

REQUIREMENTS_DEV_TXT_PATH = Path(self_path, "requirements-dev.txt")
if REQUIREMENTS_DEV_TXT_PATH.is_file():
    TESTS_REQUIRE = list(
        map(
            lambda i: i.strip(),
            REQUIREMENTS_DEV_TXT_PATH.read_text().split("\n"),
        )
    )

setup(
    name="dffml-model-tensorflow",
    version=version,
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="John Andersen",
    author_email="john.s.andersen@intel.com",
    url="https://github.com/intel/dffml/blob/master/model/tensorflow/README.md",
    license="MIT",
    keywords=[""],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    packages=find_packages(),
    entry_points={
        "dffml.model": [
            "tfdnnc = dffml_model_tensorflow.dnnc:DNNClassifierModel",
            "tfdnnr = dffml_model_tensorflow.dnnr:DNNRegressionModel",
        ]
    },
)
