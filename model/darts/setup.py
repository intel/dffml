import os
import ast
from pathlib import Path
from setuptools import find_packages, setup

ORG = "intel"
NAME = "dffml-model-darts"
DESCRIPTION = "DFFML model Darts"
AUTHOR_NAME = "Sanjiban Sengupta"
AUTHOR_EMAIL = "sanjiban.sg@gmail.com"


self_path = os.path.dirname(os.path.realpath(__file__))

with open(
    os.path.join(self_path, "dffml_model_darts", "version.py"), "r"
) as f:
    for line in f:
        if line.startswith("VERSION"):
            version = ast.literal_eval(line.strip().split("=")[-1].strip())
            break

with open(os.path.join(self_path, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="dffml-model-darts",
    version=version,
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Sanjiban Sengupta",
    author_email="sanjiban.sg@gmail.com",
    url="https://github.com/intel/dffml/blob/master/model/darts/README.md",
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
    entry_points={
        "dffml.model": [
            "dartsexponentialsmoothing = dffml_model_darts.exponentialsmoothing:ExponentialSmoothing",
        ]
    },
)
